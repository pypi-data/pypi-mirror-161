import numpy

from pyVS.Util.FileUtil import FileReaderWriter
from pyVS.pyVoxelStats.pyVoxelStats import pyVoxelStats


class Masker(pyVoxelStats):
    def __init__(self, file_type, mask_file):
        pyVoxelStats.__init__(self)
        self._file_type = file_type
        self._mask_file = mask_file
        self._fileReaderWriter = FileReaderWriter(self._file_type)
        self._mask_array = self.__read_mask()
        self._mask_ndim = self._mask_array.ndim
        self._mask_shape = self._mask_array.shape

        self.highDimMask = None
        self.ref_file = None

    def __read_mask(self):
        mask_array = self._fileReaderWriter.read_file(self._mask_file)
        return mask_array > 0.9

    def __mask_data(self, data):
        dim_dif = data.ndim - self._mask_ndim
        need_new_ref = False
        if dim_dif > 0:
            time_rep_array = [1] * data.ndim
            for dim in range(dim_dif):
                time_rep_array[dim] = data.shape[dim]
            mask = numpy.tile(self._mask_array, tuple(time_rep_array))
            if ((self.highDimMask is not None) and (mask.ndim > self.highDimMask.ndim)) or (self.highDimMask is None):
                self.highDimMask = mask
                need_new_ref = True

        elif dim_dif == 0:
            mask = self._mask_array
            need_new_ref = False
        else:
            print('Mask dimensions and data dimensions mismatch. Mask dimensions are higher than data dimension')
            return None, None
        return data[mask], need_new_ref

    def __mask_image_data(self, image_data):
        masked_data, need_new_ref = self.__mask_data(image_data)
        return masked_data, need_new_ref

    def mask_image(self, image_file):
        image_data = self._fileReaderWriter.read_file(image_file)
        masked_data, need_new_ref = self.__mask_data(image_data)
        if need_new_ref:
            self.ref_file = image_file
        return masked_data

    def __rebuild_image_data(self, data):
        if self.highDimMask is None:
            new_image_data = numpy.zeros(self._mask_array.shape, dtype=data.dtype)
            new_image_data[self._mask_array] = data
        else:
            new_image_data = numpy.zeros(self.highDimMask.shape, dtype=data.dtype)
            new_image_data[self.highDimMask] = data
        return new_image_data

    def save_image_from_data(self, data, file_name):
        new_data = self.__rebuild_image_data(data)
        if not self.mask_file:
            self.mask_file = self._mask_file
        if not self.mask_file and not self.ref_file:
            raise Exception('Error in saving file. Ref file isnt properly set.')
        if self.ref_file:
            self._fileReaderWriter.write_file(new_data, file_name, self.ref_file)
        else:
            self._fileReaderWriter.write_file(new_data, file_name, self.mask_file)

    def get_data_from_image(self, image_file_name):
        return self._fileReaderWriter.read_file(image_file_name)

    def mask_image_data(self, image_data):
        return self.__mask_image_data(image_data)
