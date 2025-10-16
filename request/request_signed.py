import json
import urllib.parse
import requests
import copy
from request_sign_generator import RequestSignGenerator


class RequestSigned(requests.Session):

    _encrypt_value: str = None
    _jsessionid: str = None

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


    def set_jsessionid(self, jsessionid: str|None):
        self._jsessionid = jsessionid
        return self


    def get_jsessionid(self):
        return {'JSESSIONID': self._jsessionid}


    def set_encrypt_value(self, encryptValue:str|None):
        self._encrypt_value = encryptValue
        return self


    def get_encrypt_value(self):
        return {'encryptValue': self._encrypt_value}


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


        if self._encrypt_value:
            request.headers.update({'encryptValue': self._encrypt_value})
        if self._jsessionid:
            request.headers.update({'JSESSION': self._jsessionid})

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
