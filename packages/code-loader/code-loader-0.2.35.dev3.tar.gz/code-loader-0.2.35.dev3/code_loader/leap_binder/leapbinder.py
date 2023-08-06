from typing import Callable, List, Optional, Dict, Any, Type

import numpy as np
import numpy.typing as npt
import inspect
from typeguard import typechecked
import tensorflow as tf

from code_loader.contract.datasetclasses import SectionCallableInterface, InputHandler, \
    GroundTruthHandler, MetadataHandler, DatasetIntegrationSetup, VisualizerHandler, PreprocessResponse, \
    PreprocessHandler, VisualizerCallableInterface, CustomLossHandler, CustomCallableInterface, PredictionTypeHandler, \
    MetadataSectionCallableInterface, UnlabeledDataPreprocessHandler
from code_loader.contract.enums import DatasetMetadataType, LeapDataType, Metric
from code_loader.visualizers.default_visualizers import DefaultVisualizer, \
    default_graph_visualizer, \
    default_image_visualizer, default_horizontal_bar_visualizer, default_word_visualizer, \
    default_image_mask_visualizer, default_text_mask_visualizer, default_raw_data_visualizer
from code_loader.utils import to_numpy_return_wrapper


class LeapBinder:
    def __init__(self) -> None:
        self.setup_container = DatasetIntegrationSetup()
        self.cache_container: Dict[str, Any] = {"word_to_index": {}}
        self._visualizer_names: List[str] = list()
        self._encoder_names: List[str] = list()
        self._extend_with_default_visualizers()

    def _extend_with_default_visualizers(self) -> None:
        self.set_visualizer(function=default_image_visualizer, name=DefaultVisualizer.Image.value,
                            visualizer_type=LeapDataType.Image)
        self.set_visualizer(function=default_graph_visualizer, name=DefaultVisualizer.Graph.value,
                            visualizer_type=LeapDataType.Graph)
        self.set_visualizer(function=default_raw_data_visualizer, name=DefaultVisualizer.RawData.value,
                            visualizer_type=LeapDataType.Text)
        self.set_visualizer(function=default_horizontal_bar_visualizer, name=DefaultVisualizer.HorizontalBar.value,
                            visualizer_type=LeapDataType.HorizontalBar)
        self.set_visualizer(function=default_word_visualizer, name=DefaultVisualizer.Text.value,
                            visualizer_type=LeapDataType.Text)
        self.set_visualizer(function=default_image_mask_visualizer, name=DefaultVisualizer.ImageMask.value,
                            visualizer_type=LeapDataType.ImageMask)
        self.set_visualizer(function=default_text_mask_visualizer, name=DefaultVisualizer.TextMask.value,
                            visualizer_type=LeapDataType.TextMask)

    @typechecked
    def set_visualizer(self, function: VisualizerCallableInterface,
                       name: str,
                       visualizer_type: LeapDataType,
                       heatmap_visualizer: Optional[Callable[..., npt.NDArray[np.float32]]] = None) -> None:
        arg_names = inspect.getfullargspec(function)[0]
        if heatmap_visualizer:
            if arg_names != inspect.getfullargspec(heatmap_visualizer)[0]:
                raise Exception(
                    f'The argument names of the heatmap visualizer callback must match the visualizer callback '
                    f'{str(arg_names)}')
        self.setup_container.visualizers.append(
            VisualizerHandler(name, function, visualizer_type, arg_names, heatmap_visualizer))
        self._visualizer_names.append(name)

    @typechecked
    def set_preprocess(self, function: Callable[[], List[PreprocessResponse]]) -> None:
        self.setup_container.preprocess = PreprocessHandler(function)

    @typechecked
    def set_unlabeled_data_preprocess(self, function: Callable[[], PreprocessResponse]) -> None:
        self.setup_container.unlabeled_data_preprocess = UnlabeledDataPreprocessHandler(function)

    @typechecked
    def set_input(self, function: SectionCallableInterface, name: str) -> None:
        function = to_numpy_return_wrapper(function)
        self.setup_container.inputs.append(InputHandler(name, function))

        self._encoder_names.append(name)

    @typechecked
    def add_custom_loss(self, function: CustomCallableInterface, name: str) -> None:
        self.setup_container.custom_loss_handlers.append(CustomLossHandler(name, function))

    @typechecked
    def add_prediction(self, name: str, labels: List[str], metrics: List[Metric],
                       custom_metrics: Optional[List[CustomCallableInterface]] = None) -> None:
        self.setup_container.prediction_types.append(PredictionTypeHandler(name, labels, metrics, custom_metrics))

    @typechecked
    def set_ground_truth(self, function: SectionCallableInterface, name: str) -> None:
        function = to_numpy_return_wrapper(function)
        self.setup_container.ground_truths.append(GroundTruthHandler(name, function))

        self._encoder_names.append(name)

    @typechecked
    def set_metadata(self, function: MetadataSectionCallableInterface, metadata_type: DatasetMetadataType,
                     name: str) -> None:
        self.setup_container.metadata.append(MetadataHandler(name, function, metadata_type))

    @typechecked
    def set_model_custom_layers(self, custom_layers: Dict[str, Type[tf.keras.layers.Layer]]):
        self.setup_container.custom_layers = custom_layers

