import requests
from request_helper import RequestHelper
from request_secret_generator import RequestSecretGenerator
from request_urls import RequestUrls


class RequestApis:

    _REQUEST_HELPER = RequestHelper()
    
    _secret_generator = ...
    _open_id = ''
    _union_id = ''

    def __init__(self,
                 open_id: str,
                 device_brand: str,
                 device_model: str,
                 device_system: str,
                 device_platform: str):

        self._secret_generator = RequestSecretGenerator(open_id,
                                                        device_brand,
                                                        device_model,
                                                        device_system,
                                                        device_platform)
        

    def get_openid(self, temp_login_code: str):

        headers = self._secret_generator.get_secret()

        return (self._REQUEST_HELPER.set_config(None, None)
                                    .post(url=RequestUrls.Url.login.get_identity,
                                          body={'code': temp_login_code},
                                          headers=headers) )


    def wechat_login(self, union_id: str, open_id: str)-> requests.Response:

        self._open_id = open_id
        self._union_id = union_id

        self._secret_generator = RequestSecretGenerator(open_id,
                                                        *self._secret_generator.get_device_info())

        body = {
            'unionId': union_id,
            'openId': open_id
        }

        headers = self._secret_generator.get_secret()

        return self._REQUEST_HELPER.post(url=RequestUrls.Url.login.wechat_login,
                                         body=body,
                                         headers=headers)


    def get_captcha(self) -> requests.Response:
        return self._REQUEST_HELPER.post(url=RequestUrls.Url.login.load_captcha)


    def login(self,
              captcha_answer: str,
              username: str,
              password: str,
              open_id: str,
              union_id: str,
              device_id: str='') -> requests.Response:

        self._open_id = open_id
        self._union_id = union_id

        device_info: tuple[str, str, str, str] = self._secret_generator.get_device_info()
        self._secret_generator = RequestSecretGenerator(open_id, *device_info)

        body = {'picCode': captcha_answer,
                'username': username,
                'password': password,
                'openId': open_id,
                'unionId': union_id,
                'model': device_info[1],
                'brand': device_info[0],
                'system': device_info[2],
                'platform': device_info[3],
                'deviceId': device_id}

        headers = self._secret_generator.get_secret()

        return self._REQUEST_HELPER.post(url=RequestUrls.Url.login.login,
                                         body=body,
                                         headers=headers)

    def check_account(self, account: str) -> requests.Response:
        return self._REQUEST_HELPER.post(url=RequestUrls.Url.common.account_status,
                                         body={'accout': account})  # DO NOT CHANGE, although spell wrong


    def get_user_info(self) -> requests.Response:
        return self._REQUEST_HELPER.post(url=RequestUrls.Url.common.user_info)


    def get_internship_plan(self, plan_id: str|None=None) -> requests.Response:
        return self._REQUEST_HELPER.post(url=RequestUrls.Url.internship.get_plan,
                                         body={'planId': plan_id} if plan_id else None)


    def get_internship_status(self, plan_id: str, moduleId: str, project_rule_id: str) -> requests.Response:

        body = {'planId': plan_id,
                'moduleId': moduleId,
                'projectRuleId': project_rule_id}

        return self._REQUEST_HELPER.post(url=RequestUrls.Url.internship.get_status,
                                         body=body)


    def get_clock_plan(self) -> requests.Response:
        return self._REQUEST_HELPER.post(url=RequestUrls.Url.clock.get_plan)


    def get_plan_details(self, trainee_id: str) -> requests.Response:
        return self._REQUEST_HELPER.post(url=RequestUrls.Url.clock.get_details,
                                         body={'traineeId': trainee_id})


    def clock_inout(self,
                    trainee_id: str,
                    adcode: str,
                    latitude: str,
                    longitude: str,
                    address: str,
                    is_clock_in: bool,
                    out_of_range: bool=False) -> requests.Response:

        device_info = self._secret_generator.get_device_info()

        body = {
            'model': device_info[1],
            'brand': device_info[0],
            'platform': device_info[3],
            'system': device_info[2],
            'openId': self._open_id,
            'unionId': self._union_id,
            'traineeId': trainee_id,
            'adcode': adcode,
            'lat': latitude,
            'lng': longitude,
            'address': address,
            'deviceName': device_info[1],
            'punchInStatus': str(int(out_of_range)),
            'clockStatus': str(int(is_clock_in) + 1)
        }

        return self._REQUEST_HELPER.post(url=RequestUrls.Url.clock.clock,
                                         body=body)


    def reclock(self,
                    trainee_id: str,
                    adcode: str,
                    latitude: str,
                    longitude: str,
                    address: str,
                    is_clock_in: bool,
                    out_of_range: bool=False) -> requests.Response:

        device_info = self._secret_generator.get_device_info()

        body = {
            'model': device_info[1],
            'brand': device_info[0],
            'platform': device_info[3],
            'system': device_info[2],
            'openId': self._open_id,
            'unionId': self._union_id,
            'traineeId': trainee_id,
            'adcode': adcode,
            'lat': latitude,
            'lng': longitude,
            'address': address,
            'deviceName': device_info[1],
            'punchInStatus': str(int(out_of_range)),
            'clockStatus': str(int(is_clock_in) + 1)
        }

        return self._REQUEST_HELPER.post(url=RequestUrls.Url.clock.reclock,
                                         body=body)

