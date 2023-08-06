import numpy as np


class LabelCoder:
    def __init__(self) -> None:
        self._code_dict = {
            None: 0
        }

    def _to_1d_(array):
        # convert to array and reshape to 1-d array
        np_arr = np.asarray(array)
        original_shape = np.shape(np_arr)

        np_arr = np.ravel(np_arr)
        return np_arr, original_shape

    def encode(self, array, return_value=True, expand=True):
        np_arr, original_shape = LabelCoder._to_1d_(array)

        if expand:
            start_code = len(self._code_dict)
            updating_code = set(np_arr) - set(self._code_dict)
            updating_code = {value: start_code + index for index, value in enumerate(updating_code)}
            self._code_dict.update(updating_code)

        if not return_value:
            return

        np_encoded = np.asarray([self._code_dict.get(value, 0) for value in np_arr])
        np_encoded = np.reshape(np_encoded, original_shape)
        return np_encoded

    def decode(self, array):
        np_arr, original_shape = LabelCoder._to_1d_(array)
        # since Python 3.7, the order of inserting to dict is preserved.
        np_codes = np.asarray(list(self._code_dict.keys()))
        # decode and reshape
        np_decoded = np_codes[np_arr]
        np_decoded = np.reshape(np_decoded, original_shape)
        return np_decoded
