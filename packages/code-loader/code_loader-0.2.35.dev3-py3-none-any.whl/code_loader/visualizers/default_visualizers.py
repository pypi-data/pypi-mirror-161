from enum import Enum

import numpy as np
import numpy.typing as npt

from code_loader.contract.visualizer_classes import LeapImage, LeapGraph, LeapHorizontalBar, LeapText, \
    LeapImageMask, LeapTextMask
from code_loader.utils import rescale_min_max


class DefaultVisualizer(Enum):
    Image = 'Image'
    Graph = 'Graph'
    HorizontalBar = 'HorizontalBar'
    Text = 'Text'
    ImageMask = 'ImageMask'
    TextMask = 'TextMask'
    RawData = 'RawData'


def default_image_visualizer(data: npt.NDArray[np.float32]) -> LeapImage:
    rescaled_data = rescale_min_max(data)
    return LeapImage(rescaled_data)


def default_graph_visualizer(data: npt.NDArray[np.float32]) -> LeapGraph:
    return LeapGraph(data)


def default_horizontal_bar_visualizer(data: npt.NDArray[np.float32]) -> LeapHorizontalBar:
    labels = [str(index) for index in range(data.shape[-1])]
    return LeapHorizontalBar(data, labels)


def default_word_visualizer(data: npt.NDArray[np.float32]) -> LeapText:
    if hasattr(data, 'tolist'):
        data = data.tolist()
    words = [str(index[0]) if type(index) is list else str(index) for index in data]
    return LeapText(words)


def default_raw_data_visualizer(data: npt.NDArray[np.float32]) -> LeapText:
    return LeapText([str(data)])


def default_image_mask_visualizer(mask: npt.NDArray[np.float32], image: npt.NDArray[np.float32]) -> LeapImageMask:
    n_different_labels = mask.shape[-1]
    labels = [str(i) for i in range(n_different_labels)]

    if len(mask.shape) > 2:
        if mask.shape[-1] == 1:
            mask = np.squeeze(mask, axis=-1)
        else:
            mask = np.argmax(mask, axis=-1)

    return LeapImageMask(mask.astype(np.uint8), image.astype(np.float32), labels)


def default_text_mask_visualizer(mask: npt.NDArray[np.float32], text_data: npt.NDArray[np.float32]) -> LeapTextMask:
    n_different_labels = mask.shape[-1]
    labels = [str(i) for i in range(n_different_labels)]

    if len(mask.shape) > 1:
        if mask.shape[-1] == 1:
            mask = np.squeeze(mask, axis=-1)
        else:
            mask = np.argmax(mask, axis=-1)

    return LeapTextMask(mask, text_data, labels)
