import logging
import requests
from src.fxxk_xiaoyoubang.apis.request_apis import XiaoyoubangApis
from exceptions import *


class Account:

    _logger = logging.getLogger(__name__)
    _api = ...

    def __init__(self, apis: XiaoyoubangApis):
        self._api = apis


    def get_info(self):
        self._logger.debug('======== 账户信息 =======')
        self._logger.info('正在获取账户信息...')

        body = self._to_json(self._api.get_user_info())

        user_info = {
            'name': body['loginer'],
            'university': body['school'],
            'major': body['specialty'],
            'department' : body['faculty'],
            'group' : body['klass'],    # NOT CHANGE, although spell wrong
        }
        self._logger.info('获取账户信息成功！')

        self._logger.debug(f'您好，{user_info['university']}的{user_info['name']}！')

        return user_info


    def _to_json(self, response: requests.Response):
        if response.status_code != 200:
            raise HttpError(f'服务器返回了{response.status_code}：{response.text}')

        elif (j:=response.json())['code'] != '200':
            raise AccountError(f'未知错误：{j['msg']}')

        else:
            return j['data']