import random
import string
import urllib.parse
import base64
import time
from twocaptcha import TwoCaptcha


def remove_duplicate(combo: list) -> list:
    new_combo = "\n".join(set(_.strip() for _ in combo))
    return new_combo.split("\n")


def parse_string(data: str, left: str, right: str) -> str:
    return data.partition(left)[-1].partition(right)[0]


def parse_recursive(data: str, left: str, right: str) -> list:
    final_list = []
    ss = data.split(left)
    for item in ss:
        amount = item.split(right)[0]
        final_list.append(amount)
        final_list.pop(0)
        final_list.pop(-1)

    return final_list


def url_encode(arg: str) -> str:
    return urllib.parse.quote(arg)


def url_decode(arg: str) -> str:
    return urllib.parse.unquote(arg)


def gen_string(length: int) -> str:
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for i in range(length))

    return random_string


def b64_encode(arg: str) -> str:
    encoded_byte = base64.b64encode(arg.encode())

    return encoded_byte.decode("UTF-8")


def b64_decode(arg: str) -> str:
    decoded_byte = base64.b64decode(arg)

    return decoded_byte.decode("UTF-8")


def get_unix_timestamp() -> int:
    return int(time.time())


'''
Bndlib currently only supports 2captcha, you can use it or you can make your own solver.
More captcha solving services will be supported in the future.
'''


class Captcha:
    def __init__(self, api_key: str) -> None:
        self.solver = TwoCaptcha(api_key)

    def recaptchaV2(self, site_key: str, url: str) -> str:
        result = self.solver.recaptcha(
            sitekey=site_key,
            url=url
        )

        return result

    def recaptchaV3(self, site_key: str, url: str) -> str:
        result = self.solver.recaptcha(
            sitekey=site_key,
            url=url,
            version='v3'
        )

        return result

    def hcaptcha(self, site_key: str, url: str) -> str:
        result = self.solver.hcaptcha(
            sitekey=site_key,
            url=url
        )

        return result

    def geetest(self, gt: str, challenge: str, url: str) -> str:
        result = self.solver.geetest(
            gt=gt,
            challenge=challenge,
            url=url
        )

        return result

    def funcaptcha(self, url: str, site_key: str) -> str:
        result = self.solver.funcaptcha(
            sitekey=site_key,
            url=url
        )

        return result
