import base64
import io

import ddddocr
from PIL import Image
import regex as re


class Captcha:

    ocr = ddddocr.DdddOcr(show_ad=False, beta=True)


    def _base64_to_image(self, base64_string: str):
        # remove jpeg base64 prefix
        base64_string = base64_string.replace('data:image/jpeg;base64,', '')

        return Image.open(io.BytesIO(base64.b64decode(base64_string)))


    def _ocr(self, image: Image.Image):
        return self.ocr.classification(image)


    def _calculate(self, expression: str):
        match = expression.replace('x', '*')
        match = match.replace('÷', '/')

        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', match)

        if match:
            # OCR's output is limited as few chars, so eval() is safe in most time
            return eval(f"{match.group(1)}{match.group(2)}{match.group(3)}")
        else:
            return None


    def get_answer(self, base64_string: str):
        source_image = self._base64_to_image(base64_string)
        expression = self._ocr(source_image)

        if expression:
            return self._calculate(expression)
        else:
            return None

