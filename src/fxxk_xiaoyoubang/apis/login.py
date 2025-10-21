import logging
import requests
from ..client.client import Client
from ..onnx_captcha.onnx_captcha import ONNXCaptcha
from ..exceptions import HttpError, CaptchaNoAnswerError
from ..exceptions.sign_errors import *


class Login:

    _logger = logging.getLogger(__name__)
    _apis = ...


    def __init__(self, apis: Client):
        self._apis = apis

    def login_password(self, captcha: str, telephone: str, password: str):
        self._logger.debug('======= 登录 =======')
        self._logger.info('正在使用密码登录...')

        response = self._apis.login(captcha_answer=captcha,
                                    username=telephone,
                                    password=password)

        if response.status_code != 200 and response.json()['msg'] == '验证码错误':
            self._logger.info('验证码错误，重新登录')
            return self.login_password(captcha, telephone, password)

        body = self._to_json(response)

        self._apis.update_config(encrypt_value=body['encryptValue'],
                                 jsessionid=body['sessionId'])

        user_id = body['loginerId']
        self._logger.info('登录成功！')

        return user_id

    def login_wechat(self):
        self._logger.debug('======= 登录 =======')
        self._logger.info('正在使用微信登录...')

        body = self._to_json(self._apis.wechat_login())

        self._apis.update_config(encrypt_value=body['encryptValue'],
                                 jsessionid=body['sessionId'])

        user_id = body['loginerId']
        self._logger.info('登录成功！')

        return user_id


    def wechat_bind_check(self):
        body = self._to_json(self._apis.check_bind())

        if body['bind'] == 'False':
            raise WeChatNotBindError('该账号没有绑定任何微信')

        return self


    def get_user_identity(self, wechat_temp_login_code: str):
        self._logger.debug('======= 鉴权 =======')
        self._logger.debug(f"微信临时登录凭证：{wechat_temp_login_code}")
        self._logger.info('获取用户登录凭证...')

        body = self._to_json(self._apis.get_identity(wechat_temp_login_code))
        open_id = body['openId']
        union_id = body['unionId']
        encrypt_value = body['encryptValue']
        session_id = body['sessionId']

        self._apis.update_config(open_id=open_id,
                                 union_id=union_id,
                                 encrypt_value=encrypt_value,
                                 jsessionid=session_id)

        self._logger.debug(f'您的凭证：OpenId={open_id}, unionId={union_id}')
        self._logger.debug(f'请求凭证：encryptValue={encrypt_value}, sessionId={session_id}')
        self._logger.info('已获取用户凭证')

        return self


    def get_captcha(self):
        self._logger.debug('======= 验证码 =======')

        self._logger.info('获取验证码...')

        image_base64 = self._to_json(self._apis.get_captcha()).replace('data:image/jpeg;base64,', '')

        self._logger.info('验证码获取成功')
        return image_base64


    def _to_json(self, response: requests.Response):
        if response.status_code != 200:
            raise HttpError(f'服务器返回了{response.status_code}：{response.text}')

        elif (j:=response.json())['code'] != '200':
            match msg:=j['msg']:
                case '不安全的请求⑥': raise DeviceCodeParsingError('devicecode校验失败')
                case '不安全的请求⑧' : raise DeviceCodeMissingError('缺少devicecode')
                case '不安全的请求⑭': raise DeviceSystemNotWindowsError('未知错误。将System设为Windows即可解决。我们仍在调查该错误。')
                case '不安全的请求' : raise DeviceCodeDecryptError('devicecode密文解密失败或签名解析失败')
                case '系统已升级，请重新打开小程序' : raise EncryptValueError('encryptValue失效')
                case '获取openid失败！' : raise WeChatTempLoginCodeError('临时登录码错误')
                case '操作失败' : raise JavaSessionError('JSESSIONID过期或其他底层事务错误')
                case _ : raise SignError(f'未知错误：{msg}')

        else:
            return j['data']
