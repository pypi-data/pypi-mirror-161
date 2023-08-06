from discord_register.discordregisterer import DiscordRegisterer
from discord_register.email_class import EmailClass
# from discord_register.phone import SmsActivate
from discord_register.exceptions import RegisterBaseException
from discord_register.utils import generate_date_of_birthday, generate_password, generate_username

from anticaptchaofficial.hcaptchaproxyless import hCaptchaProxyless
from anticaptchaofficial.hcaptchaproxyon import hCaptchaProxyon

from discord_register.exceptions import CaptchaError
from myloguru.my_loguru import get_logger


class Register:

    def __init__(
            self, email_api_key: str, captcha_api_key: str, phone_api_key: str,
            username: str = '', verbose: bool = 1, log_level: int = 20, logger=None,
            user_agent: str = '', timeout: int = 5, proxy_ip: str = '', proxy_port: str = '',
            proxy_user: str = '', proxy_password: str = ''
    ) -> None:
        self.token: str = ''
        self.birthday: str = ''
        self.password: str = ''
        self.username: str = username
        self.email_api_key: str = email_api_key
        self.captcha_api_key: str = captcha_api_key
        self.phone_api_key: str = phone_api_key
        self.verbose: bool = verbose
        self.log_level: int = log_level
        self.logger = logger or get_logger(self.log_level)
        self.user_agent: str = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
        self.timeout: int = timeout
        self.proxy_ip: str = proxy_ip
        self.proxy_port: str = proxy_port
        self.proxy_user: str = proxy_user
        self.proxy_password: str = proxy_password
        proxy: str = ''
        if all((self.proxy_ip, self.proxy_port, self.proxy_user, self.proxy_password)):
            proxy: str = f'http://{self.proxy_user}:{self.proxy_password}@{self.proxy_ip}:{self.proxy_port}/'
        self.proxy: dict = {'http': proxy, 'https': proxy} if proxy else None

    async def create(self) -> dict:
        result = {'success': False}

        try:
            email_instance: EmailClass = EmailClass(email_api_key=self.email_api_key)
            email: str = await email_instance.get_email()
            self.logger.debug(f"Got email -> {email}")
            if not self.username:
                self.username: str = generate_username()
            self.password: str = generate_password()
            self.birthday: str = generate_date_of_birthday()
            register_session: DiscordRegisterer = await DiscordRegisterer(
                proxy=self.proxy, verbose=self.verbose, email=email, password=self.password,
                username=self.username, birthday=self.birthday, user_agent=self.user_agent
            ).create_session()
            response = await register_session.register()
            if 'captcha_key' in response.text:
                website_key = response.json()['captcha_sitekey']
                captcha_key: str = await self.solve_captcha(
                    url="https://discord.com/login" ,website_key=website_key)
                response = await register_session.register(captcha_key)
            token = response.json().get('token')
            self.logger.debug(f"Got token -> {token}")

            if not token:
                self.logger.warning(f'Response: {response.text}')
                raise RegisterBaseException(text='Token not found')
            self.token: str = token
            register_session.token = token
            await register_session.check()
            self.logger.success('Checking: OK')
            email_verification_link: str = await email_instance.wait_for_email()
            email_verification_token: str = await register_session.get_email_verification_token(email_verification_link)
            email_captcha: str = await self.solve_captcha(
                url='https://discord.com/verify',
                website_key='f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34')
            response = await register_session.verify_email(email_verification_token, email_captcha)
            token = response.json().get('token')
            if not token:
                self.logger.warning(f'Response: {response.text}')
                raise RegisterBaseException(text='Token not found')
            result.update(
                {
                    'success': True,
                    'token': self.token,
                    'email': email,
                    'password': self.password
                }
            )
        except RegisterBaseException as err:
            error_text = err.text
            self.logger.error(error_text)
            result.update({'error': error_text})

        self.logger.debug(f"Got result -> {result}")
        return result

    async def solve_captcha(self, url: str, website_key: str):
        if self.proxy:
            result = await self._get_anticaptcha_with_proxy(url, website_key)
        else:
            result = await self._get_anticaptcha_without_proxy(url, website_key)

        if result == 0:
            text = f"Captcha solve error"
            raise CaptchaError(text=text)

        return result

    async def _get_anticaptcha_without_proxy(self, url: str, website_key: str) -> str:
        solver = hCaptchaProxyless()
        solver.set_verbose(self.verbose)
        solver.set_key(self.captcha_api_key)
        solver.set_website_url(url)
        solver.set_website_key(website_key)
        solver.set_soft_id(0)

        return solver.solve_and_return_solution()

    async def _get_anticaptcha_with_proxy(self, url: str, website_key: str):
        solver = hCaptchaProxyon()
        solver.set_verbose(self.verbose)
        solver.set_key(self.captcha_api_key)
        solver.set_website_url(url)
        solver.set_website_key(website_key)
        solver.set_proxy_address(self.proxy_ip)
        solver.set_proxy_port(int(self.proxy_port))
        solver.set_proxy_login(self.proxy_user)
        solver.set_proxy_password(self.proxy_password)
        solver.set_user_agent("Mozilla/5.0")
        solver.set_cookies("test=true")
        solver.set_soft_id(0)

        return solver.solve_and_return_solution()
