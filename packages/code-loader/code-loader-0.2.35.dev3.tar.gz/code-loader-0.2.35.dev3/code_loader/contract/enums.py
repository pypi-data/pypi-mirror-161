from enum import Enum, IntEnum


class Metric(Enum):
    MeanSquaredError = 'MeanSquaredError'
    MeanSquaredLogarithmicError = 'MeanSquaredLogarithmicError'
    MeanAbsoluteError = 'MeanAbsoluteError'
    MeanAbsolutePercentageError = 'MeanAbsolutePercentageError'
    Accuracy = 'Accuracy'
    BinaryAccuracy = 'BinaryAccuracy'
    MeanIOU = 'MeanIOU'


class LeapDataType(Enum):
    Image = 'Image'
    Text = 'Text'
    Graph = 'Graph'
    HorizontalBar = 'HorizontalBar'
    ImageMask = 'ImageMask'
    TextMask = 'TextMask'
    ImageWithBBox = 'ImageWithBBox'


class DatasetMetadataType(Enum):
    float = "float"
    string = "string"
    int = "int"
    boolean = "boolean"


class DataStateType(Enum):
    training = "training"
    validation = "validation"
    test = "test"
    unlabeled = "unlabeled"


class DataStateEnum(IntEnum):
    training = 0
    validation = 1
    test = 2
    unlabeled = 3


# todo: handle test not run due to error in pre process and Add to TestingSectionEnum Enum didn't run
class TestingSectionEnum(Enum):
    Warnings = "Warnings"
    Errors = "Errors"
