from abc import ABCMeta
from abc import abstractmethod
import cv2
import numpy as np


def through(x):
    return x


class AbstractPipe(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, indices):
        pass

    @abstractmethod
    def _setup(self):
        pass


class ImagePipe(AbstractPipe):
    def __init__(self, pipeline_name, image_paths, adjust_fn=through) -> None:
        self.pipeline_name = pipeline_name
        self._image_paths = image_paths
        self._adjust_fn = adjust_fn
        self._setup()
        self.data_num = len(image_paths)

    def generate(self, indices):
        return np.array([self._adjust_fn(cv2.imread(self._image_paths[i])) for i in indices])

    def _setup(self):
        for i_path in self._image_paths:
            try:
                cv2.imread(i_path)
            except BaseException:
                print(f"Cannot open {i_path}")
        print("ok")


class LabelPipe(AbstractPipe):
    def __init__(self, pipeline_name, labels, adjust_fn=through) -> None:
        self.pipeline_name = pipeline_name
        self._labels = labels
        self._adjust_fn = adjust_fn
        self.data_num = len(labels)

    def generate(self, indices):
        return np.array([self._adjust_fn(self._labels[i]) for i in indices])

    def _setup(self):
        pass
