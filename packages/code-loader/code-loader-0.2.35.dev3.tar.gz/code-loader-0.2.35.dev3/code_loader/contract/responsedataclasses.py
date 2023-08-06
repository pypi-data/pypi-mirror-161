from typing import List, Optional, Dict

from dataclasses import dataclass, field
from code_loader.contract.enums import DatasetMetadataType, LeapDataType, Metric


@dataclass
class DatasetPreprocess:
    training_length: int
    validation_length: int
    test_length: Optional[int] = None
    unlabeled_length: Optional[int] = None


@dataclass
class DatasetBaseSectionInstance:
    name: str


@dataclass
class DatasetInputInstance(DatasetBaseSectionInstance):
    shape: List[int]


@dataclass
class DatasetMetadataInstance(DatasetBaseSectionInstance):
    type: DatasetMetadataType


@dataclass
class DatasetOutputInstance(DatasetBaseSectionInstance):
    shape: List[int]


@dataclass
class VisualizerInstance:
    name: str
    type: LeapDataType
    arg_names: List[str]


@dataclass
class PredictionTypeInstance:
    name: str
    labels: List[str]
    metrics: List[Metric]
    custom_metrics: Optional[List[str]] = None


@dataclass
class DatasetSetup:
    preprocess: DatasetPreprocess
    inputs: List[DatasetInputInstance]
    metadata: List[DatasetMetadataInstance]
    outputs: List[DatasetOutputInstance]
    visualizers: List[VisualizerInstance]
    prediction_types: List[PredictionTypeInstance]
    custom_loss_names: List[str]


@dataclass
class ModelSetup:
    custom_layer_names: List[str]


@dataclass
class DatasetTestResultPayload:
    name: str
    display: Dict[str, str] = field(default_factory=dict)
    is_passed: bool = True
    shape: Optional[List[int]] = None


@dataclass
class BoundingBox:
    # (x, y) is the center of the bounding box
    x: float  # value between [0, 1], represent the percentage according to the image size.
    y: float  # value between [0, 1], represent the percentage according to the image size.

    width: float  # value between [0, 1], represent the percentage according to the image size.
    height: float  # value between [0, 1], represent the percentage according to the image size.
    confidence: float
    label: str


@dataclass
class DatasetIntegParseResult:
    payloads: List[DatasetTestResultPayload]
    is_valid: bool
    is_valid_for_model: bool
    setup: Optional[DatasetSetup] = None
    general_error: Optional[str] = None
