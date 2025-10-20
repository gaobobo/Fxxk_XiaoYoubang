import argparse
from . import clock
from . import __about__


def app():

    cli_parse = argparse.ArgumentParser(prog='Fxxk_XiaoYoubang',
                                        description='用于校友邦远程签到，适用于校友邦小程序V1.6.39。',
                                        epilog=f'{__about__.__version__}，基于{__about__.__ref__}构建。'
                                               f'构建时间：{__about__.__time__}。')

    cli_parse.add_argument('code', help='微信临时登录凭证。')
    cli_parse.add_argument('device-brand', help='设备品牌。')
    cli_parse.add_argument('device-model', help='设备型号。')
    cli_parse.add_argument('--device-system', help='设备系统，必须为Windows，否则报错。',
                           default='Windows')   # TODO: as required param in later version
    cli_parse.add_argument('device-platform', help='设备平台，可选值见左侧说明。',
                           choices=['ios', 'android', 'ohos', 'windows', 'mac'])
    cli_parse.add_argument('clock', help='进行签退还是签到。in为签到、out为签退。',
                           choices=['in', 'out'])

    cli_parse.add_argument('--username', help='可选，手机号。当指定--username与--password则使用密码登录。')
    cli_parse.add_argument('--password', help='可选，密码。当指定--username与--password则使用密码登录。')
    cli_parse.add_argument('-f', '--force', help='可选。当指定时强行覆盖签到，当签退时忽略该参数。',
                           action='store_true')
    cli_parse.add_argument('-r', '--random', help='可选。当指定时随机选择坐标。',
                           action='store_true')
    cli_parse.add_argument('-adcode', help='可选。指定签到的行政区号。默认随机生成。', type=int)
    cli_parse.add_argument('--log',
                           help='日志过滤等级。注意，DEBUG会输出隐私信息，不要在公开服务中使用DEBUG等级，'
                                '尤其是Github Action。',
                           choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                           default='WARNING')

    args = vars(cli_parse.parse_args())


    clock(code=args['code'],
         device_brand=args['device-brand'],
         device_model=args['device-model'],
         device_system=args['device_system'],
         device_platform=args['device-platform'],
         is_clock_in=(args['clock'] == 'in'),
         username=args['username'],
         password=args['password'],
         force_clock_in=args['force'],
         random_coordinates=args['random'],
         adcode=args['adcode'],
         log_level=args['log'])


if __name__ == '__main__':
    app()