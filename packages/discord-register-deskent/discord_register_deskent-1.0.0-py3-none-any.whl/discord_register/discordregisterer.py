import requests
import json
from base64 import b64encode as b

from discord_register.exceptions import ProxyError, DiscordRegistererError
from discord_register.utils import get_client_data


class DiscordRegisterer:
    def __init__(
            self, proxy: dict, verbose: bool, email: str, password: str, username: str,
            birthday: str, user_agent: str
    ) -> None:
        self.build_num: str = ''
        self.proxy: dict = proxy
        self.verbose: bool = verbose
        self.email: str = email
        self.password: str = password
        self.username: str = username
        self.birthday: str = birthday
        self.user_agent: str = user_agent
        self.token: str = ''
        self.session = requests.Session()

    async def _check_proxy(self) -> None:
        if self.proxy:
            self.session.proxies.update(self.proxy)
            try:
                self.session.get('https://ipv4.icanhazip.com/')
            except Exception as err:
                raise ProxyError(text=f'Proxy error: {err}')

    async def create_session(self) -> 'DiscordRegisterer':
        await self._check_proxy()
        self.build_num: str = get_client_data()
        try:
            response = self.session.get('https://discord.com/register')
        except Exception as err:
            raise DiscordRegistererError(text=str(err))
        self.dcfduid = response.headers['Set-Cookie'].split('__dcfduid=')[1].split(';')[0]
        self.session.cookies['__dcfduid'] = self.dcfduid
        self.sdcfduid = response.headers['Set-Cookie'].split('__sdcfduid=')[1].split(';')[0]
        self.session.cookies['__sdcfduid'] = self.sdcfduid
        self.session.cookies['locale'] = 'en'

        self.super_properties = b(json.dumps({
            "os": "Windows",
            "browser": "Firefox",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": self.user_agent,
            "browser_version": "90.0",
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": int(self.build_num),
            "client_event_source": None
        }, separators=(',', ':')).encode()).decode()

        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'en',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Content-Type': 'application/json',
            'Origin': 'https://discord.com/',
            'Referer': 'https://discord.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.user_agent,
            'X-Super-Properties': self.super_properties,
            'Cookie': '__dcfduid=' + self.dcfduid + '; __sdcfduid=' + self.sdcfduid,
            'TE': 'Trailers'
        })
        await self.get_fingerprint()

        return self

    async def get_fingerprint(self):
        response = self.session.get('https://discord.com/api/v9/experiments').json()
        self.fingerprint = response['fingerprint']
        self.session.headers.update({'x-fingerprint': response['fingerprint']})

    async def register(self, captcha_key: str = ''):
        return self.session.post(
            'https://discord.com/api/v9/auth/register',
            headers={
                'referer': 'https://discord.com/register',
                'authorization': 'undefined'
            }, json={
                'captcha_key': captcha_key if captcha_key else None,
                'consent': True,
                'date_of_birth': self.birthday,
                'email': self.email,
                'fingerprint': self.fingerprint,
                'gift_code_sku_id': None,
                'invite': None,
                'password': self.password,
                'username': self.username
            })

    async def check(self):
        check = self.session.patch('https://discord.com/api/v9/users/@me/library', headers={
            "authorization": self.token,
            'Referer': 'https://discord.com/channels/@me',
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Firefox\";v=\"91\", \"Chromium\";v=\"91\"",
            "sec-ch-ua-mobile": "?0"
        })
        if check.status_code == 403:
            raise DiscordRegistererError(text="Token locked!")
        elif check.status_code == 400:
            raise DiscordRegistererError(text=check.text)

    async def get_email_verification_token(self, link: str) -> str:
        return self.session.get(link).url.split('#token=')[1]

    async def verify_email(self, token, captcha_key):
        return self.session.post(
            'https://discord.com/api/v9/auth/verify',
            headers={
                "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Firefox\";v=\"91\", \"Chromium\";v=\"91\"",
                'referer': 'https://discord.com/verify',
                'authorization': self.token
            },
            json={
                'captcha_key': captcha_key,
                'token': token
            }
        )

    def requestSms(self, captcha_key, number):
        response = self.session.post(
            'https://discord.com/api/v9/users/@me/phone',
            headers={
                'referer': 'https://discord.com/channels/@me',
                'authorization': self.token
            },
            json={
                'captcha_key': captcha_key,
                'change_phone_reason': 'user_action_required',
                'phone': '+' + number
            }
        )
        if self.verbose:
            print(response.text)
        if response.status_code == 204:
            return True
        return False

    def submitSms(self, code, number):
        token = self.session.post(
            'https://discord.com/api/v9/phone-verifications/verify',
            headers={
                'referer': 'https://discord.com/channels/@me',
                'authorization': self.token
            },
            json={
                'code': code,
                'phone': '+' + number
            }
        ).json()
        if self.verbose:
            print(token)
        token = token['token']
        response = self.session.post(
            'https://discord.com/api/v9/users/@me/phone',
            headers={
                'referer': 'https://discord.com/channels/@me',
                'authorization': self.token
            },
            json={
                'change_phone_reason': 'user_action_required',
                'password': self.password,
                'phone_token': token
            }
        )
        if self.verbose:
            print(response.status_code)
        if response.status_code != 204:
            raise Exception("Something went wrong with SMS verification")
