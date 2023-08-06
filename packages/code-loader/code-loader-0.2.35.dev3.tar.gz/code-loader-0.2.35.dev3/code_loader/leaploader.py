from functools import lru_cache
from typing import Dict, List, Iterable, Any, Union

import numpy as np
import numpy.typing as npt

from code_loader.contract.datasetclasses import DatasetSample, DatasetBaseHandler, InputHandler, \
    GroundTruthHandler, PreprocessResponse, VisualizerHandler, VisualizerCallableReturnType, CustomLossHandler, \
    PredictionTypeHandler, MetadataHandler
from code_loader.contract.enums import DataStateEnum, TestingSectionEnum, DataStateType
from code_loader.contract.responsedataclasses import DatasetIntegParseResult, DatasetTestResultPayload, \
    DatasetPreprocess, DatasetSetup, DatasetInputInstance, DatasetOutputInstance, DatasetMetadataInstance, \
    VisualizerInstance, PredictionTypeInstance, ModelSetup
from code_loader.leap_binder import global_leap_binder
from code_loader.utils import get_root_exception_line_number, get_shape


class LeapLoader:
    def __init__(self, dataset_script: str):
        self.dataset_script: str = dataset_script

    @lru_cache()
    def exec_script(self) -> None:
        global_variables: Dict[Any, Any] = {}
        exec(self.dataset_script, global_variables)

    @lru_cache()
    def visualizer_by_name(self) -> Dict[str, VisualizerHandler]:
        self.exec_script()
        setup = global_leap_binder.setup_container
        return {
            visualizer_handler.name: visualizer_handler
            for visualizer_handler in setup.visualizers
        }

    @lru_cache()
    def custom_loss_by_name(self) -> Dict[str, CustomLossHandler]:
        self.exec_script()
        setup = global_leap_binder.setup_container
        return {
            custom_loss_handler.name: custom_loss_handler
            for custom_loss_handler in setup.custom_loss_handlers
        }

    @lru_cache()
    def prediction_type_by_name(self) -> Dict[str, PredictionTypeHandler]:
        self.exec_script()
        setup = global_leap_binder.setup_container
        return {
            prediction_type.name: prediction_type
            for prediction_type in setup.prediction_types
        }

    def get_sample(self, state: DataStateEnum, idx: int) -> DatasetSample:
        self.exec_script()
        sample = DatasetSample(inputs=self._get_inputs(state, idx),
                               gt=None if state == DataStateEnum.unlabeled else self._get_gt(state, idx),
                               metadata=self._get_metadata(state, idx),
                               index=idx,
                               state=state)
        return sample

    def check_dataset(self) -> DatasetIntegParseResult:
        test_payloads: List[DatasetTestResultPayload] = []
        setup_response = None
        general_error = None
        try:
            self.exec_script()
            preprocess_test_payload = self._check_preprocess()
            test_payloads.append(preprocess_test_payload)
            handlers_test_payloads = self._check_handlers()
            test_payloads.extend(handlers_test_payloads)
            is_valid = all([payload.is_passed for payload in test_payloads])
            setup_response = self.get_dataset_setup_response()
        except Exception as e:
            line_number = get_root_exception_line_number()
            general_error = f"Something went wrong, {repr(e)} line number: {line_number}"
            is_valid = False

        is_valid_for_model = bool(global_leap_binder.setup_container.custom_layers)

        return DatasetIntegParseResult(is_valid=is_valid, payloads=test_payloads,
                                       is_valid_for_model=is_valid_for_model, setup=setup_response,
                                       general_error=general_error)

    @staticmethod
    def _check_preprocess() -> DatasetTestResultPayload:
        preprocess_handler = global_leap_binder.setup_container.preprocess
        test_result = DatasetTestResultPayload('preprocess')
        try:
            if preprocess_handler is None:
                raise Exception('None preprocess_handler')
            preprocess_result_list = preprocess_handler.function()
            for state, preprocess_result in zip(list(DataStateType), preprocess_result_list):
                state_name = state.name
                test_result.display[state_name] = str(preprocess_result.data)
                preprocess_handler.data_length[state] = preprocess_result.length

            unlabeled_preprocess_handler = global_leap_binder.setup_container.unlabeled_data_preprocess
            if unlabeled_preprocess_handler is not None:
                unlabeled_preprocess_result = unlabeled_preprocess_handler.function()
                unlabeled_preprocess_handler.data_length = unlabeled_preprocess_result.length
                test_result.display[DataStateType.unlabeled.name] = str(unlabeled_preprocess_result.data)
        except Exception as e:
            line_number = get_root_exception_line_number()
            error_string = f"{repr(e)} line number: {line_number}"
            test_result.display[TestingSectionEnum.Errors.name] = error_string
            test_result.is_passed = False
        return test_result

    def _check_handlers(self) -> List[DatasetTestResultPayload]:
        preprocess_result = self._preprocess_result()
        result_payloads: List[DatasetTestResultPayload] = []
        idx = 0
        dataset_base_handlers: List[Union[DatasetBaseHandler, MetadataHandler]] = self._get_all_dataset_base_handlers()
        for dataset_base_handler in dataset_base_handlers:
            test_result = DatasetTestResultPayload(dataset_base_handler.name)
            for state, preprocess_response in preprocess_result.items():
                if state == DataStateEnum.unlabeled and isinstance(dataset_base_handler, GroundTruthHandler):
                    continue
                state_name = state.name
                try:
                    raw_result = dataset_base_handler.function(idx, preprocess_response)
                    test_result.display[state_name] = str(raw_result)
                    result_shape = get_shape(raw_result)
                    test_result.shape = result_shape

                    # setting shape in setup for all encoders
                    if isinstance(dataset_base_handler, (InputHandler, GroundTruthHandler)):
                        dataset_base_handler.shape = result_shape

                except Exception as e:
                    line_number = get_root_exception_line_number()
                    test_result.display[state_name] = f"{repr(e)} line number: {line_number}"
                    test_result.is_passed = False

            result_payloads.append(test_result)

        return result_payloads

    @staticmethod
    def _get_all_dataset_base_handlers() -> List[Union[DatasetBaseHandler, MetadataHandler]]:
        all_dataset_base_handlers: List[Union[DatasetBaseHandler, MetadataHandler]] = []
        all_dataset_base_handlers.extend(global_leap_binder.setup_container.inputs)
        all_dataset_base_handlers.extend(global_leap_binder.setup_container.ground_truths)
        all_dataset_base_handlers.extend(global_leap_binder.setup_container.metadata)
        return all_dataset_base_handlers

    def run_visualizer(self, visualizer_name: str, input_tensors_by_arg_name: Dict[str, npt.NDArray[np.float32]],
                       ) -> VisualizerCallableReturnType:
        return self.visualizer_by_name()[visualizer_name].function(**input_tensors_by_arg_name)

    def run_heatmap_visualizer(self, visualizer_name: str, input_tensors_by_arg_name: Dict[str, npt.NDArray[np.float32]]
                               ) -> npt.NDArray[np.float32]:
        heatmap_function = self.visualizer_by_name()[visualizer_name].heatmap_function
        if heatmap_function is None:
            assert len(input_tensors_by_arg_name) == 1
            return list(input_tensors_by_arg_name.values())[0]
        return heatmap_function(**input_tensors_by_arg_name)

    @staticmethod
    def get_dataset_setup_response() -> DatasetSetup:
        setup = global_leap_binder.setup_container
        assert setup.preprocess is not None

        unlabeled_length = None
        if global_leap_binder.setup_container.unlabeled_data_preprocess:
            unlabeled_length = global_leap_binder.setup_container.unlabeled_data_preprocess.data_length
        dataset_preprocess = DatasetPreprocess(
            training_length=setup.preprocess.data_length[DataStateType.training],
            validation_length=setup.preprocess.data_length[DataStateType.validation],
            test_length=setup.preprocess.data_length.get(DataStateType.test),
            unlabeled_length=unlabeled_length
        )

        inputs = []
        for inp in setup.inputs:
            if inp.shape is None:
                raise Exception(f"cant calculate shape for input, input name:{inp.name}")
            inputs.append(DatasetInputInstance(name=inp.name, shape=inp.shape))

        ground_truths = []
        for gt in setup.ground_truths:
            if gt.shape is None:
                raise Exception(f"cant calculate shape for ground truth, gt name:{gt.name}")
            ground_truths.append(
                DatasetOutputInstance(name=gt.name, shape=gt.shape))

        metadata = [DatasetMetadataInstance(name=metadata.name, type=metadata.type)
                    for metadata in setup.metadata]

        visualizers = [VisualizerInstance(visualizer_handler.name, visualizer_handler.type, visualizer_handler.arg_names)
                    for visualizer_handler in setup.visualizers]

        custom_loss_names = [custom_loss.name for custom_loss in setup.custom_loss_handlers]

        prediction_types = []
        for prediction_type in setup.prediction_types:
            custom_metrics_names = None
            if prediction_type.custom_metrics:
                custom_metrics_names = [custom_metric.__name__ for custom_metric in prediction_type.custom_metrics]
            pred_type_inst = PredictionTypeInstance(prediction_type.name, prediction_type.labels,
                                                    prediction_type.metrics, custom_metrics_names)
            prediction_types.append(pred_type_inst)

        return DatasetSetup(preprocess=dataset_preprocess, inputs=inputs, outputs=ground_truths, metadata=metadata,
                            visualizers=visualizers, prediction_types=prediction_types,
                            custom_loss_names=custom_loss_names)

    @staticmethod
    def get_model_setup_response() -> ModelSetup:
        setup = global_leap_binder.setup_container
        return ModelSetup(list(setup.custom_layers.keys()))

    @lru_cache()
    def _preprocess_result(self) -> Dict[DataStateEnum, PreprocessResponse]:
        preprocess = global_leap_binder.setup_container.preprocess
        # TODO: add caching of subset result
        assert preprocess is not None
        preprocess_results = preprocess.function()
        preprocess_result_dict = {
            DataStateEnum(i): preprocess_result
            for i, preprocess_result in enumerate(preprocess_results)
        }

        unlabeled_preprocess = global_leap_binder.setup_container.unlabeled_data_preprocess
        if unlabeled_preprocess is not None:
            preprocess_result_dict[DataStateEnum.unlabeled] = unlabeled_preprocess.function()

        return preprocess_result_dict

    def _get_dataset_handlers(self, handlers: Iterable[DatasetBaseHandler],
                              state: DataStateEnum, idx: int) -> Dict[str, npt.NDArray[np.float32]]:
        result_agg = {}
        preprocess_result = self._preprocess_result()
        preprocess_state = preprocess_result[state]
        for handler in handlers:
            handler_result = handler.function(idx, preprocess_state)
            handler_name = handler.name
            result_agg[handler_name] = handler_result
        return result_agg

    def _get_inputs(self, state: DataStateEnum, idx: int) -> Dict[str, npt.NDArray[np.float32]]:
        return self._get_dataset_handlers(global_leap_binder.setup_container.inputs, state, idx)

    def _get_gt(self, state: DataStateEnum, idx: int) -> Dict[str, npt.NDArray[np.float32]]:
        return self._get_dataset_handlers(global_leap_binder.setup_container.ground_truths, state, idx)

    def _get_metadata(self, state: DataStateEnum, idx: int) -> Dict[str, Union[str, int, bool, float]]:
        result_agg = {}
        preprocess_result = self._preprocess_result()
        preprocess_state = preprocess_result[state]
        for handler in global_leap_binder.setup_container.metadata:
            handler_result = handler.function(idx, preprocess_state)
            handler_name = handler.name
            result_agg[handler_name] = handler_result

        return result_agg
