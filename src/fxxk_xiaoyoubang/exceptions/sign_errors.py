from .xyb_exception import XYBException

class SignError(XYBException): pre = 'SIGN'
class DeviceCodeParsingError(SignError): code = 10
class DeviceCodeMissingError(SignError): code = 11
class DeviceSystemNotWindowsError(SignError): code = 12
class DeviceCodeDecryptError(SignError): code = 20
class EncryptValueError(SignError): code = 30
class JavaSessionError(SignError): code = 40
class WeChatTempLoginCodeError(SignError): code = 31
class WeChatNotBindError(SignError): code = 32
