from .xyb_exception import XYBException

class OnnxError(XYBException): pre = 'ONNX'
class CaptchaNoAnswerError(OnnxError): code = 10
class InitOnnxError(OnnxError): code = 20

