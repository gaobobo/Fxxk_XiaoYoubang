import requests
from .apis.request_helper import RequestHelper
from .apis.request_urls import RequestUrls
from fxxk_xiaoyoubang.request.devicecode_generator import RequestSecretGenerator


class XiaoyoubangApis:

    _open_id = ''
    _union_id = ''
    _device_brand = ''
    _device_model = ''
    _device_system = ''
    _device_platform = ''

    _request_helper = RequestHelper()
    _secret_generator = ...


    def __init__(self, device_brand, device_model, device_system, device_platform):
        self.update_config(device_brand=device_brand,
                           device_model=device_model,
                           device_system=device_system,
                           device_platform=device_platform)

    def update_config(self,
                      open_id: str|None = None,
                      union_id: str|None = None,
                      device_brand: str|None = None,
                      device_model: str|None = None,
                      device_system: str|None = None,
                      device_platform: str|None = None,
                      encrypt_value: str|None = None,
                      jsessionid: str|None = None,):

        self._open_id = open_id or self._open_id
        self._union_id = union_id or self._union_id
        self._device_brand = device_brand or self._device_brand
        self._device_model = device_model or self._device_model
        self._device_system = device_system or self._device_system
        self._device_platform = device_platform or self._device_platform

        self._secret_generator = RequestSecretGenerator(self._open_id,
                                                        self._device_brand,
                                                        self._device_model,
                                                        self._device_system,
                                                        self._device_platform)

        if encrypt_value or jsessionid:
            old_encrypt_value, old_jsessionid = tuple(self._request_helper.get_config().values())
            self._request_helper.set_config(encrypt_value=encrypt_value or old_encrypt_value,
                                            jsessionid=jsessionid or old_jsessionid)

        return self


    def get_config(self):

        encrypt_value, jsessionid = tuple(self._request_helper.get_config().values())

        return {'open_id': self._open_id,
                'union_id': self._union_id,
                'device_brand': self._device_brand,
                'device_model': self._device_model,
                'device_system': self._device_system,
                'device_platform': self._device_platform,
                'encrypt_value': encrypt_value,
                'jsessionid': jsessionid,}
        

    def get_identity(self, temp_login_code: str):

        headers = self._secret_generator.get_secret()

        return (self._request_helper.set_config(None, None)
                                    .post(url=RequestUrls.Url.login.get_identity,
                                          body={'code': temp_login_code},
                                          headers=headers) )

    def check_bind(self,
                  union_id: str|None = None,
                  open_id: str|None = None) -> requests.Response:

        self.update_config(union_id=union_id, open_id=open_id)

        body = {
            'unionId': self._union_id,
            'openId': self._open_id
        }

        return self._request_helper.post(url=RequestUrls.Url.login.check_if_bind_wechat,
                                         body=body)



    def wechat_login(self,
                     union_id: str|None = None,
                     open_id: str|None = None)-> requests.Response:

        self.update_config(union_id=union_id, open_id=open_id)

        body = {
            'unionId': self._union_id,
            'openId': self._open_id
        }

        headers = self._secret_generator.get_secret()

        return self._request_helper.post(url=RequestUrls.Url.login.wechat_login,
                                         body=body,
                                         headers=headers)


    def get_captcha(self) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.login.load_captcha)


    def login(self,
              captcha_answer: str,
              username: str,
              password: str,
              open_id: str|None = None,
              union_id: str|None = None,
              device_id: str='') -> requests.Response:

        self.update_config(union_id=union_id, open_id=open_id)

        body = {'picCode': captcha_answer,
                'username': username,
                'password': password,
                'openId': self._open_id,
                'unionId': self._union_id,
                'model': self._device_model,
                'brand': self._device_brand,
                'system': self._device_system,
                'platform': self._device_platform,
                'deviceId': device_id}

        headers = self._secret_generator.get_secret()

        return self._request_helper.post(url=RequestUrls.Url.login.login,
                                         body=body,
                                         headers=headers)

    def check_account(self, account: str) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.common.account_status,
                                         body={'accout': account})  # DO NOT CHANGE, although spell wrong


    def get_user_info(self) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.common.user_info)


    def get_internship_plan(self, plan_id: str|None=None) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.internship.get_plan,
                                         body={'planId': plan_id} if plan_id else None)


    def get_internship_status(self, plan_id: str, moduleId: str, project_rule_id: str) -> requests.Response:

        body = {'planId': plan_id,
                'moduleId': moduleId,
                'projectRuleId': project_rule_id}

        return self._request_helper.post(url=RequestUrls.Url.internship.get_status,
                                         body=body)


    def get_clock_plan(self) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.clock.get_plan)


    def get_default_clock_plan(self, plan_id: str) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.clock.get_default_plan,
                                         body={'planId': plan_id})


    def get_plan_details(self, trainee_id: str) -> requests.Response:
        return self._request_helper.post(url=RequestUrls.Url.clock.get_details,
                                         body={'traineeId': trainee_id})


    def clock_inout(self,
                    trainee_id: str,
                    adcode: str,
                    latitude: str,
                    longitude: str,
                    address: str,
                    is_clock_in: bool,
                    out_of_range: bool=False) -> requests.Response:

        body = {
            'model': self._device_model,
            'brand': self._device_brand,
            'platform': self._device_platform,
            'system': self._device_system,
            'openId': self._open_id,
            'unionId': self._union_id,
            'traineeId': trainee_id,
            'adcode': adcode,
            'lat': latitude,
            'lng': longitude,
            'address': address,
            'deviceName': self._device_model,
            'punchInStatus': int(out_of_range),
            'clockStatus': int(is_clock_in) + 1
        }

        headers = self._secret_generator.get_secret()

        return self._request_helper.post(url=RequestUrls.Url.clock.clock,
                                         body=body, headers=headers)


    def reclock(self,
                    trainee_id: str,
                    adcode: str,
                    latitude: str,
                    longitude: str,
                    address: str,
                    is_clock_in: bool,
                    out_of_range: bool=False) -> requests.Response:

        body = {
            'model': self._device_model,
            'brand': self._device_brand,
            'platform': self._device_platform,
            'system': self._device_system,
            'openId': self._open_id,
            'unionId': self._union_id,
            'traineeId': trainee_id,
            'adcode': adcode,
            'lat': latitude,
            'lng': longitude,
            'address': address,
            'deviceName': self._device_model,
            'punchInStatus': int(out_of_range),
            'clockStatus': int(is_clock_in) + 1
        }

        headers = self._secret_generator.get_secret()

        return self._request_helper.post(url=RequestUrls.Url.clock.reclock,
                                         body=body, headers=headers)

