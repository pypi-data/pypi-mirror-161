from typing import List
from typing import Union

import numpy as np

import pyaaware


class Predict:
    def __init__(self, name: str) -> None:
        self._predict = pyaaware._Predict(name)

    @property
    def file_name(self) -> str:
        return self._predict.get_file_name()

    @property
    def input_shape(self) -> List[int]:
        return self._predict.get_input_shape()

    @property
    def output_shape(self) -> List[int]:
        return self._predict.get_output_shape()

    @property
    def flattened(self) -> bool:
        return self._predict.is_flattened()

    @property
    def timestep(self) -> bool:
        return self._predict.has_timestep()

    @property
    def channel(self) -> bool:
        return self._predict.has_channel()

    @property
    def mutex(self) -> bool:
        return self._predict.is_mutex()

    @property
    def feature(self) -> Union[str, None]:
        result = self._predict.get_feature()
        if not result:
            return None
        return result

    def execute(self, x: np.ndarray) -> np.ndarray:
        y = self._predict.execute(x.ravel())
        return np.reshape(y, self.output_shape)
