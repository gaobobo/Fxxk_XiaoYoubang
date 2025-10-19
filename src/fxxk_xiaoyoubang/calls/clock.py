import logging
import math
import random
import requests
from fxxk_xiaoyoubang.apis.client import Client
from ..exceptions import HttpError, ClockError


class Clock:

    _logger = logging.getLogger(__name__)
    _apis = ...

    trainne_id: str = ...
    address: str = ...
    latitude: float = ...
    longitude: float = ...
    accept_range: float = ...
    is_clock_in: bool = ...
    is_clock_out: bool = ...


    def __init__(self, api: Client):
        self._api = api


    def clock_in(self, adcode: str | None=None, force_clock=False, random_position=False):

        self._logger.debug('======= 签到 =======')

        if adcode is None:
            self._logger.warning(f'没有指定行政区编号，将自动随机生成')
            adcode = random.randint(100000, 999999)

        if random_position:
            self._logger.warning(f'已选择随机位置，会在200m内随机选择位置签到')
            self.random_coordinates()

        if self.is_clock_out:
            self._logger.warning('已完成完整的签到、签退，跳过本次签到。已签退不支持重新签到。')
        elif force_clock and self.is_clock_in:
            self._logger.warning(f'您已签到，将强制重新签到。这会覆盖签到记录。')
            self._to_json(self._api.reclock(trainee_id=self.trainne_id,
                                            adcode=adcode,
                                            latitude=str(self.latitude),
                                            longitude=str(self.longitude),
                                            address=self.address,
                                            is_clock_in=True) )
        else:
            self._logger.info('正在签到...')
            self._to_json(self._api.clock_inout(trainee_id=self.trainne_id,
                                                adcode=adcode,
                                                latitude=str(self.latitude),
                                                longitude=str(self.longitude),
                                                address=self.address,
                                                is_clock_in=True) )
            self._logger.debug(f'签到地址：{self.address}({self.latitude},{self.longitude})，{adcode}')

        self._logger.info('成功！')


    def clock_out(self, adcode: str | None=None, random_position=False):

        self._logger.debug('======= 签退 =======')

        if adcode is None:
            self._logger.warning(f'没有指定行政区编号，将自动随机生成')
            adcode = random.randint(100000, 999999)

        if random_position:
            self._logger.warning(f'已选择随机位置，会在200m内随机选择位置签到')
            self.random_coordinates()

        if self.is_clock_out:
            self._logger.warning('已签退。跳过本次签到。')
        else:
            self._logger.info('正在签退...')
            self._to_json(self._api.clock_inout(trainee_id=self.trainne_id,
                                                adcode=adcode,
                                                latitude=str(self.latitude),
                                                longitude=str(self.longitude),
                                                address=self.address,
                                                is_clock_in=False) )
            self._logger.debug(f'签退地址：{self.address}({self.latitude},{self.longitude})，{adcode}')

        self._logger.info('成功！')


    def get_clock_plans(self, plan_id: str):
        self._logger.debug('======= 获取签到计划 =======')
        self._logger.info('正在获取签到计划...')

        body = self._to_json(self._api.get_default_clock_plan(plan_id))

        if body['hasMore'] == 'True':
            self._logger.warning(f'计划“{body['clockVo']['planName']}”似乎有多个项目。'
                                 f'您当前的项目是“{body['clockVo']['projectName']}”，如不是，请在小程序或网页申请切换项目。')

        self.trainne_id = body['clockVo']['traineeId']

        self._logger.debug(f'当前项目：{body['clockVo']['planName']}，当前计划：{body['clockVo']['projectName']}')
        self._logger.info('获取签到计划成功！')

        return self


    def get_position(self):
        self._logger.debug('======= 获取签到位置 =======')
        self._logger.info('正在获取位置...')

        body = self._to_json(self._api.get_plan_details(self.trainne_id))

        if body['needTakePhoto'] == 'True':
            self._logger.warning('该计划要求拍照。本脚本不支持上传照片，将跳过该计划的签到。')
            return None
        if body['nonWorkingDay'] == 'True':
            self._logger.warning('该计划可以跳过节假日。本脚本不会判断是否在节假日，仍将尝试签到。')

        self.address = body['postInfo']['address']
        self.latitude = body['postInfo']['lat']
        self.longitude = body['postInfo']['lng']
        self.accept_range = float(body['postInfo']['distance'])
        self.is_clock_in = int(body['clockInfo']['status']) < 2
        self.is_clock_out = int(body['clockInfo']['status']) < 1

        self._logger.debug(f'签到位置：{self.address}')
        self._logger.debug(f'经纬度：({self.latitude}, {self.longitude})')
        self._logger.debug(f'可接受的最大距离：{self.accept_range}')
        self._logger.debug(f'状态：{'已' if self.is_clock_in else '未'}签到，{'已' if self.is_clock_out else '未'}签退')
        self._logger.info('获取签到位置成功！')

        return self


    def random_coordinates(self, distance: float=200):
        earth_r = 6371000

        random_distance = distance * math.sqrt(random.random())
        random_angle = random.uniform(0, 2 * math.pi)

        delta = random_distance / earth_r

        lat_rad = math.radians(self.latitude)
        lon_rad = math.radians(self.longitude)

        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(delta) +
            math.cos(lat_rad) * math.sin(delta) * math.cos(random_angle)
        )

        new_lon_rad = lon_rad + math.atan2(
            math.sin(random_angle) * math.sin(delta) * math.cos(lat_rad),
            math.cos(delta) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )

        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)

        self.latitude = round(new_lat, 12)
        self.longitude = round(new_lon, 14)

        return self


    def _to_json(self, response: requests.Response):
        if response.status_code != 200:
            raise HttpError(f'服务器返回了{response.status_code}：{response.text}')

        elif (j := response.json())['code'] != '200':
            raise ClockError(f'未知错误：{j['msg']}')

        else:
            return j['data']