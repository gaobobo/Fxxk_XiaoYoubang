import logging
import requests
from src.fxxk_xiaoyoubang.apis.request_apis import XiaoyoubangApis
from exceptions import *


class Internship:

    _logger = logging.getLogger(__name__)
    _apis = ...


    def __init__(self, apis: XiaoyoubangApis):
        self._apis = apis


    def get_internship_plan(self):
        self._logger.info('======= 获取实习计划 =======')
        self._logger.debug('正在获取实习计划...')

        body = self._to_json(self._apis.get_internship_plan())
        plans = [(i['planName'], i['planId']) for i in body]

        if len(plans) > 1:
            self._logger.warning(f'您多个实习计划，所有符合条件的都将自动签到')

        self._logger.debug(f'您的实习计划有：{plans}')
        self._logger.info('获取实习计划成功！')

        return plans


    def _to_json(self, response: requests.Response):
        if response.status_code != 200:
            raise HttpError(f'服务器返回了{response.status_code}：{response.text}')

        elif (j := response.json())['code'] != '200':
            raise InternshipError(f'未知错误：{j['msg']}')

        else:
            return j['data']