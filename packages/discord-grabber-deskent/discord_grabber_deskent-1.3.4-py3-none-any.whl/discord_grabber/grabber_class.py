# -*- coding: UTF-8 -*-
import asyncio
import time

from random import randint, choice
from typing import Dict, Union

import aiohttp
import requests as requests
from myloguru.my_loguru import get_logger
from pydantic import BaseModel, EmailStr
from anticaptchaofficial.hcaptchaproxyon import hCaptchaProxyon
from anticaptchaofficial.hcaptchaproxyless import hCaptchaProxyless

from discord_grabber.mail_reader import MailReader
from .exceptions import *


class UserModel(BaseModel):
    email: EmailStr
    password: str


class TokenGrabber:
    """
    Класс принимает и валидирует е-мэйл и пароль от аккаунта дискорда и
    возвращает словарь с токеном, дискорд_ид и настройками дискорда.
    Автоматически проходит капчу если она требуется.

    Attributes
        email: str
            Will be validated as EmailStr by pydandic

        password: str

        anticaptcha_key: str = ''
            API key for https://anti-captcha.com/

        two_captcha_key: str = ''
            API key for https://2captcha.com/

        log_level: int [Optional] = 20
            by default: 20 (INFO)

        proxy: str [Optional] = ''
             example: proxy = "http://user:pass@10.10.1.10:3128/"

        proxy_ip: str = ''

        proxy_port: str = ''

        proxy_user: str = ''

        proxy_password: str = ''

        user_agent: str [Optional] =
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
        (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"

        logger=None
            By default will be used my_loguru logger by Deskent

            (pip install myloguru-deskent)

        max_tries: int = 12
            Maximum amount of tries for getting captcha.

            :pause: between tries 10 seconds.

        timeout: int = 5
            Maximum time of request waiting (seconds).

        pause: int = 10
            Delay between tries for requesting API token answer (seconds).

        verbose: bool = 0
            Anticaptcha logging

    Methods
        get_token
    """

    def __init__(
            self, email: str, password: str, anticaptcha_key: str = '', two_captcha: str = '',
            proxy: str = '', log_level: int = 20, user_agent: str = '', logger=None,
            max_tries: int = 12, timeout: int = 5, pause: int = 10, proxy_ip: str = '',
            proxy_port: str = '', proxy_user: str = '', proxy_password: str = '',
            verbose: bool = 0
    ):
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(timeout=timeout)
        self.user = UserModel(email=email, password=password)
        self.anticaptcha_key: str = anticaptcha_key
        self.two_captcha: str = two_captcha
        self.verbose: bool = verbose
        self.headers: dict = {}
        self.fingerprint: str = ''
        self.proxy: str = proxy
        self.proxy_ip: str = proxy_ip
        self.proxy_port: str = proxy_port
        self.proxy_user: str = proxy_user
        self.proxy_password: str = proxy_password
        self.max_tries: int = max_tries
        self.timeout: int = timeout
        self.pause: int = pause
        self.logger = logger if logger else get_logger(log_level)
        self.user_agent: str = user_agent or (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"
        )

    async def get_token(self) -> Dict[str, str]:
        """
        :return: dict: {'token': '...'} if no error else {'error': ...}
        """

        server_postfix: str = self.user.email.split('@')[-1]
        self.email_server = f'imap.{server_postfix}'

        return await self._get_token()

    async def _get_token(self) -> Dict[str, str]:
        result = {'email': self.user.email}
        if not self.session.closed:
            await self.session.close()
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            self.session: aiohttp.ClientSession = session
            try:
                self._update_headers()
                await self._update_fingerprint()
                self.headers.update({'X-Fingerprint': self.fingerprint})
                token_data: dict = await self._get_token_data()
                result.update(**token_data)

            except GrabberBaseException as err:
                error_text = err.text
                self.logger.error(error_text)
                result.update({'error': error_text})

            return result

    def _update_headers(self) -> None:
        self.logger.debug("Getting headers...")
        self.headers.update(
            {'accept': '*/*', 'accept-language': 'ru,en;q=0.9',
             'authorization': 'undefined',
             'content-type': 'application/json', 'origin': 'https://discord.com',
             'referer': 'https://discord.com/login', 'user-agent': self.user_agent,
             'x-super-properties': self.__get_xsuperproperties()}
        )
        self.logger.success("Getting headers... OK")

    async def _update_fingerprint(self) -> None:
        self.logger.debug("Getting fingerprint...")
        params = {
            'url': "https://discord.com/api/v9/experiments",
            'headers': self.headers
        }
        response: Dict[str, str] = await self._send_request(params)
        self.fingerprint = response.get("fingerprint")
        if not self.fingerprint:
            self.logger.exception(f'Getting fingerprint... FAIL')
            raise FingerPrintError
        self.logger.success("Getting fingerprint... OK")

    async def _resolve_captcha(self, captcha_sitekey: str) -> str:
        self.logger.debug(f'Капча для {self.user.email}, отправляю запрос на решение')
        if self.two_captcha:
            return await self._get_two_captcha_token(captcha_sitekey)
        elif self.anticaptcha_key:
            return await self._get_anticaptcha(captcha_sitekey)
        raise CaptchaAPIkeyError("No captcha API key found")

    async def _get_token_data(self) -> Dict[str, str]:

        self.logger.debug("Getting token...")
        response: Dict[str, str] = await self._authenticate()
        self.logger.debug(f"Authenticate response: {response}")
        if response.get('token'):
            self.logger.success("Getting token...OK")
            return response
        captcha_sitekey: str = response.get('captcha_sitekey')
        if captcha_sitekey:
            captcha_result: str = await self._resolve_captcha(captcha_sitekey)
            response: Dict[str, str] = await self._authenticate(captcha_result)
        self.logger.debug(f"Captcha authenticate response: {response}")
        if response.get('token'):
            self.logger.success("Getting token... OK")
            return response
        response_text = str(response)
        if 'ACCOUNT_LOGIN_VERIFICATION_EMAIL' in response_text:
            return await self._verify_email()
        elif 'INVALID_LOGIN' in response_text:
            error_text = f'Неверная пара Email-пароль: {self.user.email}:{self.user.password}'
        elif 'ACCOUNT_PERMANENTLY_DISABLED' in response_text:
            error_text = f'Учётная запись была отключена: {self.user.email}:{self.user.password}'
        elif 'ACCOUNT_COMPROMISED_RESET_PASSWORD' in response_text:
            error_text = 'Смените пароль, чтобы войти.'
        elif 'EMAIL_TYPE_INVALID_EMAIL' in response_text:
            error_text = 'Некорректно указан адрес электронной почты.'
        else:
            error_text = f'Undefined error: {response_text}'
        self.logger.error(error_text)

        return {'error': error_text}

    async def _verify_email(self) -> Dict[str, str]:
        for delay in range(3):
            time.sleep(delay + 1)
            status: int = await self.__verify_email()
            if status == 204:
                response: dict = await self._authenticate()
                self.logger.debug(f"Authenticate response: {response}")
                if response.get('token'):
                    self.logger.success("Getting token...OK")
                    return response
        error_text = f'Требуется подтверждение по почте для {self.user.email}'
        self.logger.error(error_text)
        return {'error': error_text}

    async def __verify_email(self) -> int:
        mail_answer: str = MailReader(
            email=self.user.email, password=self.user.password, logger=self.logger
        ).start()
        if mail_answer.startswith('error'):
            raise MailReaderError(text=mail_answer)
        answer = requests.get(mail_answer)
        token: str = answer.request.url.split('=')[-1]
        data = {'token': token}
        response_approve = requests.post(
            url='https://discord.com/api/v9/auth/authorize-ip',
            json=data,
            headers=self.headers
        )
        status: int = response_approve.status_code
        self.logger.debug(f"Mail approve status code: {status}\n{response_approve.text}")
        self.logger.debug("Try get token again...")

        return status

    async def _authenticate(self, captcha_key: str = '') -> Dict[str, str]:
        self.logger.debug("Authenticating...")
        data = {
            'fingerprint': self.fingerprint,
            'email': self.user.email,
            'password': self.user.password
        }
        if captcha_key:
            data.update(captcha_key=captcha_key)
            self.logger.debug(f"_authenticate data:\n{data}")
        params = dict(
            url='https://discord.com/api/v9/auth/login',
            headers=self.headers,
            json=data,
        )
        response: Dict[str, str] = await self._send_request(params=params, method='post')
        if response:
            self.logger.success("Authenticating...OK")
        else:
            self.logger.error(f"Authenticating...FAIL: {response}")

        return response

    async def _send_request(self, params: dict, method: str = 'get') -> Dict[str, str]:
        if self.proxy:
            params.update(proxy=self.proxy)
        params.update(ssl=False, timeout=self.timeout)
        async with self.session.request(method=method, **params) as response:
            try:
                data: dict = await response.json()
                if data.get('message') == 'The resource is being rate limited.':
                    pause_time: float = data.get('retry_after', 0)
                    await asyncio.sleep(pause_time)
                    return await self._send_request(params, method)
                return data
            except asyncio.exceptions.TimeoutError as err:
                self.logger.exception(err)
                raise RequestError(text='Timeout error')
            except Exception as err:
                self.logger.exception(err)
                response_text: str = await response.text()
                self.logger.debug(response_text)
                raise RequestError(text=response_text)

        return {}

    async def _get_two_captcha_id(self, site_key: str) -> str:
        url = (
            f"http://2captcha.com/in.php?key={self.two_captcha}"
            f"&method=hcaptcha"
            f"&sitekey={site_key}"
            f"&pageurl=https://discord.com/login&json=1"
        )
        response_id: dict = await self._send_request(params=dict(url=url))
        id_: str = response_id.get("request", '')
        if id_ == 'ERROR_WRONG_USER_KEY':
            raise CaptchaAPIkeyError
        return id_

    async def __get_two_captcha_token(self, id_: str) -> str:
        url = (
            f"http://2captcha.com/res.php?key={self.two_captcha}"
            f"&action=get"
            f"&json=1"
            f"&id={id_}"
        )
        self.logger.debug(f"Pause {self.pause} seconds")
        await asyncio.sleep(self.pause)
        for index, _ in enumerate(range(self.max_tries), start=1):
            response_token: dict = await self._send_request(params=dict(url=url))
            self.logger.debug(f"Try №{index}/{self.max_tries}: {response_token}")
            status: int = response_token.get('status')
            token: str = response_token.get('request')
            if status and token:
                return token
            self.logger.debug(f"Next try after {self.pause} seconds")
            await asyncio.sleep(self.pause)
        else:
            raise CaptchaTimeoutError

    async def _get_two_captcha_token(self, captcha_sitekey: str) -> str:
        self.logger.debug("Getting captcha...")
        self.logger.debug(f"Captcha_sitekey: {captcha_sitekey}")
        captcha_id: str = await self._get_two_captcha_id(captcha_sitekey)
        captcha_result: str = await self.__get_two_captcha_token(captcha_id)
        self.logger.debug(f'Ответ от капчи пришел:\n{captcha_result}')
        self.logger.success("Getting captcha...OK")

        return captcha_result

    def __get_xsuperproperties(self) -> str:
        browser_vers = f'{randint(10, 99)}.{randint(0, 9)}.{randint(1000, 9999)}.{randint(10, 99)}'
        xsuperproperties = {
            "os": choice(['Windows', 'Linux']), "browser": "Chrome", "device": "",
            "system_locale": choice(['ru', 'en', 'ua']), "browser_user_agent": self.user_agent,
            "browser_version": browser_vers,
            "os_version": choice(['xp', 'vista', '7', '8', '8.1', '10', '11']), "referrer": "",
            "referring_domain": "", "referrer_current": "", "referring_domain_current": "",
            "release_channel": "stable", "client_build_number": "10" + str(randint(1000, 9999)),
            "client_event_source": "null"
        }
        return str(xsuperproperties)

    async def _get_anticaptcha(self, website_key: str) -> str:
        if all((self.proxy_ip, self.proxy_port, self.proxy_user, self.proxy_password)):
            return await self.__get_anticaptcha_with_proxy(website_key)
        return await self.__get_anticaptcha_without_proxy(website_key)

    async def __get_anticaptcha_with_proxy(self, website_key: str):
        self.logger.info('Getting captcha. Please wait...')
        solver = hCaptchaProxyon()
        solver.set_verbose(self.verbose)
        solver.set_key(self.anticaptcha_key)
        solver.set_website_url("https://discord.com/login")
        solver.set_website_key(website_key)
        solver.set_proxy_address(self.proxy_ip)
        solver.set_proxy_port(int(self.proxy_port))
        solver.set_proxy_login(self.proxy_user)
        solver.set_proxy_password(self.proxy_password)
        solver.set_user_agent("Mozilla/5.0")
        solver.set_cookies("test=true")
        solver.set_soft_id(0)

        result: Union[int, str] = solver.solve_and_return_solution()
        if result == 0:
            text = f"Task finished with error {solver.error_code}"
            raise CaptchaAPIkeyError(text)

        return result

    async def __get_anticaptcha_without_proxy(self, website_key: str) -> str:
        solver = hCaptchaProxyless()
        solver.set_verbose(self.verbose)
        solver.set_key(self.anticaptcha_key)
        solver.set_website_url("https://discord.com/login")
        solver.set_website_key(website_key)

        solver.set_soft_id(0)

        result: Union[int, str] = solver.solve_and_return_solution()
        if result == 0:
            text = f"Task finished with error {solver.error_code}"
            raise CaptchaAPIkeyError(text)

        return result
