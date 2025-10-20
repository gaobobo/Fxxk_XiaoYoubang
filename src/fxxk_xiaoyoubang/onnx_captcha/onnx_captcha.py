import numpy
import onnxruntime
import numpy as np
from PIL import Image
import io
import base64
import pickle
import re
from importlib import resources
from . import models, tools


class ONNXCaptcha:

    _CAPTCHA_CHAR_SET = [''] + list('0123456789+-x/=?')

    _onnx_session = ...
    _model_charset: dict[int, str] = ...

    def __init__(self,
                 model_path=str(resources.files(models) / 'DdddOcr-common.onnx'),
                 charset_path=str(resources.files(tools) / 'tools/charset.pkl')) :

        self._onnx_session = onnxruntime.InferenceSession(model_path)

        with open(charset_path, "rb") as f:
            charset = pickle.load(f)
            charset_specific = {charset[i]: i for i in self._CAPTCHA_CHAR_SET}

            self._model_charset = charset_specific


    def _base64_to_image(self, base64_string: str) -> Image.Image:
        # remove jpeg base64 prefix
        base64_string = base64_string.replace('data:image/jpeg;base64,', '')

        return Image.open(io.BytesIO(base64.b64decode(base64_string)))

    def _image_preprocess(self, image: Image.Image, resize_height: int=64) -> Image.Image:
        image = image.convert('L')

        width, height = image.size
        resize_ratio = float(resize_height) / height
        resize_width = int(width * resize_ratio)

        image = image.resize((resize_width, resize_height),
                             Image.Resampling.BILINEAR)

        return image


    def _image_flatten(self, image: Image.Image) -> np.ndarray:
        image_np = np.array(image).astype('float32')
        image_np = image_np / 255.0

        # Convert to (Channel, Height, Width)
        if len(image_np.shape) == 2:
            image_np = image_np[np.newaxis, ...]    # (Height, Width) -> (Channel, Height, Width)
        else:
            image_np = image_np.transpose(2, 0, 1)  # (Height, Width, Channel) -> (Channel, Height, Width)

        image_np = image_np[np.newaxis, ...]    # (Batch, ...)

        return image_np


    def _model_predict(self, image_array: np.ndarray) -> np.ndarray:
        model_input_name = self._onnx_session.get_inputs()[0].name

        output = self._onnx_session.run(None, {model_input_name: image_array})[0]
        predict_result = np.argmax(output[:, 0, :], axis=1) # (sequency, 1, classes) -> (seq_length, possible_class)

        return predict_result


    def _ctc_decode(self, predict_result: np.ndarray) -> str | None:

        # No text found
        if predict_result is None or predict_result.size == 0:
            return None

        # Only 1 char
        if predict_result.size == 1:
            return self._model_charset[predict_result[0]]

        # ignore repeating index
        valid_diff_mask = np.r_[True,   # always save first element
                                predict_result[1:] != predict_result[:-1]]  # compare this and next element

        # ignore blank char
        valid_non_blank_mask = predict_result != 0

        # ignore un-specific char
        valid_index_mask = numpy.isin(predict_result, list(self._model_charset.keys()))

        # merge mask
        valid = valid_index_mask & valid_diff_mask & valid_non_blank_mask

        predict_result = predict_result[valid]

        return ''.join([self._model_charset[i] for i in predict_result])


    def predict(self, base64_image: str) -> str:

        image = self._base64_to_image(base64_image)
        image = self._image_preprocess(image)
        image = self._image_flatten(image)

        predict_result = self._model_predict(image)

        return self._ctc_decode(predict_result)


    def get_answer(self, ocr_result: str) -> str | None:

        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', ocr_result)

        if match:
            # OCR's output is limited as few chars, so eval() is safe in most time
            return eval(f"{match.group(1)}{match.group(2)}{match.group(3)}")
        else:
            return None
