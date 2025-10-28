import random
import time
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import fxxk_xiaoyoubang as xyb
from fxxk_xiaoyoubang import __about__ as xyb_build_info
import os
from .captcha import Captcha
import configparser
from pathlib import Path


force_clock_in = bool(os.getenv('FORCE_CLOCK_IN'))
clock_distance = int(os.getenv('CLOCK_DISTANCE'))
adcode = int(os.getenv('ADCODE') or random.randint(100000, 999999))
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

scheduler = BlockingScheduler(timezone=os.getenv('TZ'))
client = xyb.Client(device_brand=os.getenv('DEVICE_BRAND'),
                    device_model=os.getenv('DEVICE_MODEL'),
                    device_system=os.getenv('DEVICE_SYSTEM'),
                    device_platform=os.getenv('DEVICE_PLATFORM'))
main_logger = logging.getLogger('app')
xyb_logger = logging.getLogger('fxxk_xiaoyoubang')
captcha = Captcha()
config = configparser.ConfigParser()
config_path = Path('config.ini')


def read_config():
    try:
        config.read(config_path, encoding="utf-8")
    except:
        main_logger.exception("无法读取配置或配置损坏。可能没有建立配置？")


def save_config():
    try:
        main_logger.info('保存凭据中...')

        config["time"] = {"update": str(int(time.time()))}
        config["xyb"] = client.get_config()

        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)

    except:
        main_logger.exception("保存配置失败。跳过本次保存。")


def get_token():
    main_logger.info('刷新凭据中...')
    if username and password:
        main_logger.warning("已传入USERNAME与PASSWORD，将使用密码鉴权。")

        for _ in range(10):
            captcha_answer = captcha.get_answer(xyb.Login(client).get_captcha())

            if captcha_answer: break

            main_logger.warning("验证码识别失败。1秒后重试。")
            time.sleep(1)

        else:
            raise RuntimeError("验证码多次识别失败")

        xyb.Login(client).login_password(telephone=os.getenv('USERNAME'),
                                         password=os.getenv('PASSWORD'),
                                         captcha=captcha_answer)

    else:
        xyb.Login(client).login_wechat()


def refresh_token():
    try:
        get_token()

        save_config()

        main_logger.info(f'已安排下次执行：{scheduler.get_job('refresh_token').next_run_time}。')

    except:
        main_logger.exception(f'该任务出错，将安排至10分钟后重新执行。')
        scheduler.add_job(func=refresh_token,
                          id='refresh_token_retry',
                          trigger='date',
                          run_date=datetime.now(scheduler.timezone) + timedelta(minutes=10),
                          replace_existing=True)


def clock_in():
    try:
        xyb.Account(client).get_info()
        plans = xyb.Internship(client).get_internship_plan()
        for _,plan_id in plans:
            xyb.Clock(client).get_clock_plans(plan_id).get_position().clock_in(adcode=adcode,
                                                                               force_clock=force_clock_in,
                                                                               random_distance=clock_distance)

        main_logger.info(f'已安排下次执行：{scheduler.get_job('clock_in').next_run_time}。')

    except:
        main_logger.exception(f'该任务出错，将安排至10分钟后重新执行。')
        scheduler.add_job(func=clock_in,
                          id='clock_in_retry',
                          trigger='date',
                          run_date=datetime.now(scheduler.timezone) + timedelta(minutes=10),
                          replace_existing=True)


def clock_out():
    try:
        xyb.Account(client).get_info()
        plans = xyb.Internship(client).get_internship_plan()
        for _,plan_id in plans:
            xyb.Clock(client).get_clock_plans(plan_id).get_position().clock_out(adcode=adcode,
                                                                                random_distance=clock_distance)

        main_logger.info(f'已安排下次执行：{scheduler.get_job('clock_out').next_run_time}。')

    except:
        main_logger.exception(f'该任务出错，将安排至10分钟后重新执行。')
        scheduler.add_job(func=clock_out,
                          id='clock_out_retry',
                          trigger='date',
                          run_date=datetime.now(scheduler.timezone) + timedelta(minutes=10),
                          replace_existing=True)


def app():

    log_level = getattr(logging, os.getenv("LOG").upper(), None)

    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'))

    main_logger.addHandler(ch)
    main_logger.setLevel(log_level)

    xyb_logger.addHandler(ch)
    xyb_logger.setLevel(log_level)

    if log_level == logging.DEBUG:
        main_logger.warning("你正在以DEBUG模式运行，这会输出隐私信息。不要在任何公开服务使用该模式运行。")

    main_logger.info("程序已启动。")
    main_logger.info(f'构建信息：{xyb_build_info.__ref__}-{xyb_build_info.__time__}。')

    if not (os.getenv('DEVICE_BRAND') 
            and os.getenv('DEVICE_MODEL') 
            and os.getenv('DEVICE_SYSTEM') 
            and os.getenv('DEVICE_PLATFORM')):
        main_logger.critical("没有指定设备信息。请重新建立容器并指定DEVICE_BRAND、DEVICE_MODEL、DEVICE_PLATFORM")
        raise RuntimeError("DEVICE INFO ENV NOT SPECIFIC!")


    if config_path.exists():

        read_config()

        last_launch_time = datetime.fromtimestamp(int(config["time"]["update"])).astimezone(scheduler.timezone)

        if datetime.now(tz=scheduler.timezone).hour - last_launch_time.hour > 1:
            main_logger.warning("该容器自上次启动已经超过1个小时，这可能导致登录凭据过期。"
                                "如果频繁失败，请重新获取微信登录码并重新建立容器。")

        main_logger.info(f"Welcome! 上次启动时间：{last_launch_time.strftime('%Y/%m/%d %H:%M:%S')}。")

        main_logger.info('读取配置...')
        client.update_config(open_id=config["xyb"]["open_id"],
                             union_id=config["xyb"]["union_id"],
                             encrypt_value=config["xyb"]["encrypt_value"],
                             jsessionid=config["xyb"]["jsessionid"])

        main_logger.debug(client.get_config())

    else:
        if os.getenv('WECHAT_TEMP_CODE'):
            main_logger.info("首次启动，正在获取身份信息...")
            xyb.Login(client).get_user_identity(os.getenv('WECHAT_TEMP_CODE'))

        else:
            main_logger.critical('没有找到临时登录码。请重新建立容器并指定WECHAT_TEMP_CODE。')
            raise RuntimeError("ENV WECHAT_TEMP_CODE NOT FOUND!")

    main_logger.info("尝试首次鉴权...")
    get_token()
    save_config()

    main_logger.info("启动完成。建立定时任务...")

    try:
        time_refresh_token = int(os.getenv('REFRESH_TIME_MIN'))
        time_clock_in_hour = int(os.getenv('CLOCK_IN_TIME_HOUR'))
        time_clock_in_minute = int(os.getenv('CLOCK_IN_TIME_MIN'))
        time_clock_out_hour = int(os.getenv('CLOCK_OUT_TIME_HOUR'))
        time_clock_out_minute = int(os.getenv('CLOCK_OUT_TIME_MIN'))
    except (ValueError, TypeError):
        main_logger.critical(f"指定了时间，但似乎不是数字。请重新建立容器并指定REFRESH_TIME_MIN、CLOCK_IN_TIME_HOUR、"
                             f"CLOCK_IN_TIME_MIN、CLOCK_OUT_TIME_HOUR、CLOCK_OUT_TIME_MIN。")
        raise RuntimeError("TIME FORMATE ERROR!")

    main_logger.debug(f"将要新建的任务："
                      f"刷新凭据：每{time_refresh_token}分钟执行一次；"
                      f"签退：每天的{time_clock_out_hour:02}:{time_clock_out_minute:02}；"
                      f"签到：每天的{time_clock_in_hour:02}:{time_clock_in_minute:02}。"
                      f"以上时间基于时区{scheduler.timezone}。")

    scheduler.add_job(func=refresh_token,
                      id='refresh_token',
                      trigger='interval',
                      minutes=time_refresh_token)

    scheduler.add_job(func=clock_in,
                      id='clock_in',
                      trigger='cron',
                      hour=time_clock_in_hour,
                      minute=time_clock_in_minute)

    scheduler.add_job(func=clock_out,
                      id='clock_out',
                      trigger='cron',
                      hour=time_clock_out_hour,
                      minute=time_clock_out_minute)

    main_logger.info("任务建立完成。")
    main_logger.info("将进程交给apscheduler，goodbye！")

    scheduler.start()
