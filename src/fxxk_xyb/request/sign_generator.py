import hashlib
import random
import time
import urllib.parse
import regex as re


class RequestSignGenerator:

    # from XiaoYoubang WeChat Mini-app client, although some are duplicated
    _EXCLUDE_FIELDS = [
        "content", "deviceName", "keyWord", "blogBody", "blogTitle", "getType", "responsibilities", "street", "text",
        "reason", "searchvalue", "key", "answers", "leaveReason", "personRemark", "selfAppraisal", "imgUrl", "wxname",
        "deviceId", "avatarTempPath", "file", "file", "model", "brand", "system", "deviceId", "platform", "code",
        "openId", "unionid", "clockDeviceToken", "clockDevice", "address", "name", "enterpriseEmail",
        "responsibilities", "practiceTarget", "guardianName", "guardianPhone", "practiceDays", "linkman",
        "enterpriseName", "companyIntroduction", "accommodationStreet", "accommodationLongitude",
        "accommodationLatitude", "internshipDestination", "specialStatement", "enterpriseStreet", "insuranceName",
        "insuranceFinancing", "policyNumber", "overtimeRemark", "riskStatement", "specialStatement"
    ]

    _CLIENT_VERSION = '1.6.39'

    _key = ...
    _index = ...
    _timestamp = ...


    def __init__(self,
                 key:str='5bfAJQgalpsqH4LQg16QZvwbce22mlEgGHIrosd57xtJSTFvw4890KE340mrin',
                 key_index:list[int]=random.sample(range(62), 20),
                 timestamp:int=int(time.time())):

        self._key = key
        self._index = key_index
        self._timestamp = timestamp


    def _get_random_key(self) -> str:
        return "".join(self._key[i] for i in self._index)


    def _get_string(self, body: dict[str, str]) -> str:
        body = {i: body[i] for i in body if i not in self._EXCLUDE_FIELDS}
        body = {i: body[i] for i in sorted(body)}   # sorted by keys, fit server signature algorithm

        values = body.values()

        # remove all output including punctuation marks
        regex_sort_marks = re.compile(r"[`~!@#$%^&*()+=|{}':;',\[\].<>/?~！@#￥%……&*（）——+|{}【】‘；：”“’。，、？]")
        output = "".join([i for i in values if not (regex_sort_marks.search(i) or i == '""')])

        # remove CJK Unicode char
        # output = re.sub('[\\u4E00-\\u9FFF]+', '', output)    # WeChat client jump this
        # output = re.sub(r'\p{Han}+', '', output)

        # remove empty space
        output = re.sub(r"\s+", '', output)

        # remove [<, >, &, -]
        output = re.sub(r"[<>&-]", '', output)    # duplicated with \p{S}+

        # remove emojis or like emojis
        # output = re.sub("\uD83C[\uDF00-\uDFFF]|\uD83D[\uDC00-\uDE4F]", '', output)
        output = re.sub(r"\p{Extended_Pictographic}+", '', output)

        return output


    def get_signature(self, body: dict[str, str] | None) -> dict[str, str]:
        data = (self._get_string(body) if body else '') + str(self._timestamp) + self._get_random_key()
        data = urllib.parse.quote(data, safe='')

        md5 = hashlib.md5(data.encode('utf-8')).hexdigest()
        secret = '_'.join(map(str, self._index))
        timestamp = str(self._timestamp)

        return {'m': md5,
                't': timestamp,
                's': secret,
                'v': self._CLIENT_VERSION,
                'n': ','.join(self._EXCLUDE_FIELDS)}