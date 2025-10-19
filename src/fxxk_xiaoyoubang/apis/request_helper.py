import requests
from .request_apis import RequestUrls as apiUrls
from ..request.request_signed import RequestSigned

class RequestHelper:

    _HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Version/4.0 '
                              'Chrome/138.0.7204.180 '
                              'Mobile Safari/537.36 '
                              'XWEB/1380243 '
                              'MMWEBSDK/20250904 '
                              'MMWEBID/2341 '
                              'MicroMessenger/8.0.64.2940(0x28004035) '
                              'WeChat/arm64 '
                              'Weixin NetType/WIFI '
                              'Language/zh_CN '
                              'ABI/arm64 '
                              'miniProgram/wx9f1c2e0bbc10673c',
                'xweb_xhr': '1',
                'wechat': '1',
                'Referer': r'https://servicewechat.com/wx9f1c2e0bbc10673c/529/page-frame.html',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                }

    _REQUEST_SESSION = RequestSigned()
    _host = ...


    def __init__(self, host: str = apiUrls.Host.base):
        self._REQUEST_SESSION.headers.update(self._HEADERS)
        self._host = host


    def set_config(self, encrypt_value:str|None, jsessionid:str|None):
        self._REQUEST_SESSION.encrypt_value = encrypt_value
        self._REQUEST_SESSION.jsessionid = jsessionid
        return self


    def get_config(self):
        return {'encryptValue': self._REQUEST_SESSION.encrypt_value,
                'JSESSION': self._REQUEST_SESSION.jsessionid}


    def get(self, url:str, headers: dict[str, str]|None=None) -> requests.Response:
        headers = self._HEADERS | (headers or {})
        return self._REQUEST_SESSION.get(self._host + url, headers=headers)


    def post(self, url: str,
             body: dict[str, str]|None=None,
             as_json=False,
             headers: dict[str, str]|None=None) -> requests.Response:

        headers = self._HEADERS | (headers or {})

        if as_json or body is None:
            return self._REQUEST_SESSION.post(self._host + url, json=body or {}, headers=headers)

        else:
            return self._REQUEST_SESSION.post(self._host + url, data=body, headers=headers)

