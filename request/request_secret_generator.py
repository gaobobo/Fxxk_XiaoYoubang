import random
import time
from gmssl import sm2


class RequestSecretGenerator:

    _PUBLIC_KEY = ('A3C35DE075A2E86F28D52A41989A08E740A82FB96D43D9AF8A5509E0A4E837EC'
                   'B384C44FE1EE95F601EF36F3C892214D45C9B3F75B57556466876AD6052F0F1F')
    _UID_CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    # Use same conic section params as client
    _SM2_ECC_CONFIG = {
        'n': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123',
        'p': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF',
        'g': '32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7'
             'bc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0',
        'a': 'FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC',
        'b': '28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93',
    }

    _client_appid = ...
    _device_describe = ...
    _openid = ...

    def __init__(self,
                 user_openId: str,
                 device_brand:str,
                 device_model:str,
                 device_system:str,
                 device_platform:str,
                 appid:str='wx9f1c2e0bbc10673c'):

        self._client_appid = appid
        self._device_describe = ','.join([device_brand,device_model,device_system,device_platform])
        self._openid = user_openId


    def _generate_uid(self):
        return ''.join([self._UID_CHARSET[random.randint(0, len(self._UID_CHARSET) - 1)] for _ in range(16)])


    def get_secret(self):
        encrypt_string = (f'b|_{self._device_describe}'
                         f'aid|_{self._client_appid}'
                         f't|_{int(time.time() * 1000)}'
                         f'uid|_{self._generate_uid()}'
                         f'oid|_{self._openid}')

        sm2_crypt = sm2.CryptSM2(public_key=self._PUBLIC_KEY,
                                 private_key=None, mode=1)
        secret = sm2_crypt.encrypt(encrypt_string.encode('utf-8'))

        secret = secret.hex()

        if secret.startswith('04'): secret = secret[2:]

        return {'devicecode': secret}

