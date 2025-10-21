import logging
import fxxk_xiaoyoubang as xyb


def clock(code: str,
          device_brand: str,
          device_model: str,
          device_system: str,
          device_platform: str,
          is_clock_in: bool,
          force_clock_in: bool = False,
          random_coordinates: bool = False,
          adcode: int|None = None,
          log_level: str = 'WARNING'):

    log_level = getattr(logging, log_level, None)

    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    xyb.logger.setLevel(log_level)
    xyb.logger.addHandler(ch)

    client = xyb.Client(device_brand=device_brand,
                        device_model=device_model,
                        device_system=device_system,
                        device_platform=device_platform,)

    xyb.Login(client).get_user_identity(code).wechat_bind_check().login_wechat()

    xyb.Account(client).get_info()

    plans = xyb.Internship(client).get_internship_plan()

    for _, id in plans:
        clock = xyb.Clock(client).get_clock_plans(id).get_position()

        if is_clock_in :
            clock.clock_in(adcode, force_clock_in, random_coordinates)
        else:
            clock.clock_out(adcode, random_coordinates)

