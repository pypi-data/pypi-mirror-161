from collections import Iterable, OrderedDict
from typing import Union

import numpy as np

from .coordinate_generator import CoordinateGeneratorABC
from .util import central_crop


class WeightedPatchPicker:
    """
    An iterable for picking a patch from data. The original data can be a single numpy.ndarray or a set of data.
    """

    def __init__(self, data: Union[tuple, list, np.ndarray, dict], patch_size, coordinates: CoordinateGeneratorABC):
        self.data = data
        self.patch_size = patch_size
        self.index = 0
        self.coordinates = coordinates

    def reset(self):
        self.coordinates.regenerate()
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        index = self.index
        self.index += 1

        if index >= len(self):
            raise StopIteration

        if isinstance(self.data, Iterable):
            # If the data is a bundle of samples, all ndarray data will be cropped according the candidate coordinate.
            if isinstance(self.data, dict):
                results = OrderedDict()
                for k, v in self.data.items():
                    if isinstance(v, np.ndarray):
                        results[k] = central_crop(v, self.coordinates[index], self.patch_size)
                    else:
                        results[k] = v
                return results

            results = []
            for data in self.data:
                if isinstance(data, np.ndarray):
                    results.append(central_crop(data, self.coordinates[index], self.patch_size))
                else:
                    results.append(data)
            return tuple(results)
        return central_crop(self.data, self.coordinates[index], self.patch_size)

    def __len__(self):
        return len(self.coordinates)
