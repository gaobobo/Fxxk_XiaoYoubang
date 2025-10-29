import json
import urllib.parse
import requests
import copy
from .sign_generator import RequestSignGenerator
import logging


class RequestSigned(requests.Session):

    encrypt_value: str|None = None
    jsessionid: str|None = None

    _logger = logging.getLogger(__name__)

    def __init__(self, base: requests.Session=requests.Session()):
        super().__init__()

        # copy requests.Session config
        self.headers.update(copy.deepcopy(base.headers))
        self.cookies.update(copy.deepcopy(base.cookies))
        self.auth = copy.deepcopy(base.auth)
        self.proxies = copy.deepcopy(base.proxies)
        self.verify = base.verify
        self.cert = base.cert
        self.trust_env = base.trust_env

        # copy connection pool
        for prefix, adapter in base.adapters.items():
            self.mount(prefix, copy.deepcopy(adapter))


    def _sign_request(self, request: requests.PreparedRequest) -> requests.PreparedRequest:

        if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            body = dict(urllib.parse.parse_qsl(request.body, keep_blank_values=True))
            signature = RequestSignGenerator().get_signature(body)

            # For key-value formate body, need to use RFC 3986 standard, not HTML Form. For example,
            # space need to escape as `%20` not `+` .
            body = urllib.parse.urlencode(body, quote_via=urllib.parse.quote, safe='')
            request.body = body

            request.headers['Content-Length'] = str(len(request.body.encode('utf-8')))

        elif request.headers['Content-Type'] == 'application/json':
            body = json.loads(request.body)
            signature = RequestSignGenerator().get_signature(body)

        else:
            signature = RequestSignGenerator().get_signature(None)

        request.headers.update(signature)


        if self.encrypt_value:
            request.headers.update({'encryptValue': self.encrypt_value})
        if self.jsessionid:
            request.headers.update({'Cookie': f'JSESSIONID={self.jsessionid}'})

        self._logger.debug(f"当前请求的请求头：{request.headers}")

        return request
        

    def send(
        self,
        request,
        *,
        stream = ...,
        verify = ...,
        proxies = ...,
        cert = ...,
        timeout = ...,
        allow_redirects = ...,
        **kwargs,
    ) -> requests.Response:

        request_signed = self._sign_request(request)
        received_response = super().send(request_signed)

        return received_response
