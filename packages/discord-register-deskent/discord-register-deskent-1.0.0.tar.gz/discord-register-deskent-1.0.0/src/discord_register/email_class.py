import requests
import time

from discord_register.exceptions import EmailError


class EmailClass:
    def __init__(self, email_api_key: str) -> None:
        self.email_api_key = email_api_key
        self.id: str = ''
        self.email: str = ''

    async def get_email(self):
        url = (
            f'https://api.kopeechka.store/mailbox-get-email?api=2.0'
            f'&spa=1'
            f'&site=discord.com'
            f'&sender=discord'
            f'&regex=&mail_type='
            f'&token={self.email_api_key}'
        )
        r = await self._send_request(url)
        response: dict = r.json()
        if response.get('status') != 'OK':
            raise EmailError(text=r.text)
        self.id = response['id']
        self.email = response['mail']

        return self.email

    async def check_email(self) -> str:
        url = (
            f'https://api.kopeechka.store/mailbox-get-message?full=1'
            f'&spa=1'
            f'&id={self.id}'
            f'&token={self.email_api_key}'
        )
        r = await self._send_request(url)
        response: dict = r.json()
        return response['value']

    async def delete_email(self):
        url = f'https://api.kopeechka.store/mailbox-cancel?id={self.id}&token={self.email_api_key}'
        await self._send_request(url)

    async def wait_for_email(self) -> str:
        for _ in range(30):
            time.sleep(2)
            value: str = await self.check_email()
            if value != 'WAIT_LINK':
                await self.delete_email()
                return value.replace('\\', '')

    @staticmethod
    async def _send_request(url: str, method: str = "GET") -> requests.Response:
        return requests.request(method=method, url=url)
