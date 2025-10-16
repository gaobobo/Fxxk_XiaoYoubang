from dataclasses import dataclass


@dataclass(frozen=True)
class RequestUrls:
    class Host:
        base = 'https://xcx.xybsyw.com'
        app = 'https://app.xybsyw.com'

    class Url:
        class login:
            load_captcha = '/school/common/plugins/loadCaptcha.action'
            get_identity = '/common/getOpenId.action'
            login = '/login/login.action'
            wechat_login = '/login/login!wx.action'

        class common:
            account_status = '/login/checkAccount.action'
            user_info = '/account/LoadAccountInfo.action'

        class internship:
            get_plan = '/student/progress/loadMyPractice.action'
            get_status = '/student/progress/ProjectProgressInfo.action'

        class clock:
            get_plan = '/student/clock/GetPlan.action'
            get_details = '/clock/GetPlan!detail.action'
            clock = '/student/clock/Post.action'
            reclock = '/student/clock/Post!updateClock.action'