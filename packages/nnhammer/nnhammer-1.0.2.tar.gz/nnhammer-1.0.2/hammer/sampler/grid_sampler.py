from typing import Union

import numpy as np
import torch
import torch.nn.functional as F
from hammer.sampler.util import central_crop, get_margin

from hammer.sampler.coordinate_generator import GridCoordinateGenerator


class GridSampler:
    """
    Perform grid sample and recovery. The last N dimensions of given data will be split.
    """

    def __init__(self, data: Union[np.ndarray, torch.Tensor], patch_shape, valid_shape=None):
        """
        Args:
            data: The data needs to be sample.
            patch_shape: The data will be divided into patches with the shape of patch_shape.
            valid_shape: The valid shape of a patch, used for restore.
        """
        self.patch_shape = np.asarray(patch_shape, dtype=np.uint32)
        self.valid_shape = np.asarray(valid_shape, dtype=np.uint32) if valid_shape else self.patch_shape
        assert len(self.patch_shape.shape) == len(self.valid_shape.shape)

        self.full_shape = data.shape
        # Shape of data, but batch and/or channel dimensions are excluded.
        self.original_shape = self.full_shape[-len(self.patch_shape):]
        self.coordinate_generator = GridCoordinateGenerator(self.original_shape, patch_shape=self.patch_shape,
                                                            valid_shape=self.valid_shape)

        if not (self.patch_shape == self.valid_shape).all():
            if isinstance(data, torch.Tensor):
                pad_size = tuple(np.flip(self.coordinate_generator.padding_size, axis=0).flatten())
                self.padded_data = F.pad(data, pad=pad_size, mode="constant", value=0)
            else:
                pad_size = self.coordinate_generator.padding_size
                if len(self.full_shape) != len(self.valid_shape):
                    extra_dimensions = [[0, 0]] * (len(self.full_shape) - len(self.valid_shape))
                    pad_size = np.concatenate((np.asarray(extra_dimensions, dtype=np.int32), pad_size))
                self.padded_data = np.pad(data, pad_width=pad_size, mode='constant', constant_values=0)
        else:
            self.padded_data = data
        self.index = 0

    def restore(self, blocks, restore_shape=None):
        """
        Every element's batch/channel dimensions in blocks should be put at the beginning.
        Args:
            blocks:
            restore_shape: Restore data's batch/channel dimensions can differ from the data which was divided
            as long as keeping the same image dimensions.
        """
        blocks = list(map(lambda x: self._shrink_shape(x), blocks))
        if not restore_shape:
            restore_shape = self.full_shape
        return self._rebuild_image(blocks, restore_shape)

    def _shrink_shape(self, data: Union[np.ndarray, torch.Tensor]):
        """
        Shrink data to assigned shape.
        """
        if (self.patch_shape == self.valid_shape).all():
            return data
        center = [e // 2 if e % 2 != 0 else e // 2 - 1 for e in self.valid_shape]
        center = np.asarray(center)
        center = center + self.coordinate_generator.padding_size[:, 0]
        cropped = central_crop(data, center, self.valid_shape)
        return cropped

    def _rebuild_image(self, blocks, restore_shape):
        assert len(blocks) > 0
        assert len(self.coordinate_generator.valid_central_coordinates) == len(blocks)
        result = np.zeros(shape=restore_shape, dtype=blocks[0].dtype) if isinstance(blocks[0], np.ndarray) \
            else torch.zeros(size=restore_shape, dtype=blocks[0].dtype, device=blocks[0].device)

        block_margin = get_margin(self.valid_shape)
        margin = block_margin[:, 0][None, :]
        coordinates = self.coordinate_generator.valid_central_coordinates - margin
        extra_dimensions = [slice(None)] * (len(restore_shape) - len(self.valid_shape))
        for i, block in enumerate(blocks):
            slice_sequence = extra_dimensions + \
                             [slice(coordinates[i, j], coordinates[i, j] + self.valid_shape[j])
                              for j in range(len(self.valid_shape))]

            result[tuple(slice_sequence)] = block
        return result

    def __len__(self):
        return len(self.coordinate_generator)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self):
            raise StopIteration

        patch = central_crop(self.padded_data, self.coordinate_generator[self.index], self.patch_shape)
        self.index += 1
        return patch
