import json
import random
import asyncio

from base64 import b64encode
from typing import Dict, Union

import requests
from urllib3 import disable_warnings
from anticaptchaofficial.hcaptchaproxyon import hCaptchaProxyon

from myloguru import get_logger
from discord_joiner.exceptions import *

disable_warnings()


class DiscordJoiner:
    """
    Adds user token by invite link to discord server
    using proxy (optional)

        Attributes
        token: str
            Discord account token will be joined

        invite_link: str
            Invite link to channel

        log_level: int [Optional] = 20
            by default: 20 (INFO)

        proxy: dict [Optional] = None
             example: proxy = {
                "http": "http://user:pass@10.10.1.10:3128/",
                "https": "https://user:pass@10.10.1.10:3128/",

                }
        user_agent: str [Optional] =
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
        (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"

        delay: int [Optional] = 2
            Delay between requests, in seconds

        logger=None
            By default will be used my_loguru logger by Deskent

            (pip install myloguru-deskent)

    Methods
        join
            returns: bool
    """

    def __init__(
            self, token: str, invite_link: str, proxy: dict = None, proxy_ip: str = '',
            proxy_port: str = '', proxy_user: str = '', proxy_password: str = '',
            delay: float = 2, user_agent: str = '', log_level: int = 20,
            logger=None, anticaptcha_key: str = ''
    ) -> None:
        self.anticaptcha_key: str = anticaptcha_key
        self.token: str = token
        self.__headers: dict = {}
        self.__invite_link: str = invite_link
        self.session: 'requests.Session' = requests.Session()
        self.__locale: str = ''
        self.__invite_id: str = ''
        self.__discord_username: str = ""
        self._proxy: dict = proxy
        self.proxy_ip: str = proxy_ip
        self.proxy_port: str = proxy_port
        self.proxy_user: str = proxy_user
        self.proxy_password: str = proxy_password
        if all((proxy_ip, proxy_port, proxy_user, proxy_password)):
            self._proxy: dict = {
                'http': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}/',
                'https': f'http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}/',
            }
        self.__xsuperproperties: bytes = b''
        self.delay: float = delay
        self.logger = logger if logger else get_logger(log_level)
        self._user_agent = user_agent or ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                          "(KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36")

    async def _check_proxy(self) -> bool:
        if not isinstance(self._proxy, dict):
            raise ProxyError(text=f"Proxy myst be dict, got {type(self._proxy)}.")
        if not self._proxy:
            return True
        params = {
            'url': "https://ifconfig.me/all.json",
            'proxies': self._proxy
        }
        answer: 'requests.Response' = await self._send_request(params)
        status: int = answer.status_code
        if status != 200:
            raise ProxyError(text=f'Proxy check status code: {status}')
        answer_data: dict = answer.json()
        ip_addr: str = answer_data.get("ip_addr", '')
        proxy_ip: str = self._proxy.get('http').split('@')[-1].split(':')[0]
        if ip_addr == proxy_ip:
            return True

    async def _update_proxy(self) -> None:
        if self._proxy:
            self.session.proxies.update(proxies=str(self._proxy))
            self.logger.debug("\n\tProxy updated: OK")

    async def __get_headers(self) -> None:
        self.session.headers.update(
            {
                'user-agent': self._user_agent, 'accept': '*/*',
                'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7',
                'content-type': 'application/json',
                'origin': 'https://discord.com', 'referer': self.__invite_link,
                'x-super-properties': self.__xsuperproperties
            }
        )
        self.logger.debug("\n\tHeaders: OK")

    async def __get_finger_print(self) -> None:
        params = {
            "url": "https://discord.com/api/v7/experiments",
            "verify": False
        }
        response: 'requests.Response' = await self._send_request(params)
        if response and response.status_code == 200:
            fingerprint = json.loads(response.text)["fingerprint"]
            self.session.headers.update({'X-Fingerprint': fingerprint,
                                         'x-discord-locale': self.__locale,
                                         'authorization': self.token})
            self.logger.debug(f'\n\tFingerPrints: OK')
            return
        response_text = '' if not response else response.text
        self.logger.debug(f'\n\tFingerPrints: ERROR: {response_text}')
        raise FingerprintError(text=response_text)

    async def __authorization(self) -> None:
        params = {
            "url": 'https://discordapp.com/api/v9/users/@me',
            "verify": False
        }
        response: 'requests.Response' = await self._send_request(params)
        if response and 'username' in json.loads(response.text):
            self.__discord_username = json.loads(response.text)['username']
            self.logger.debug(f'\n\tAuthorization: @{self.__discord_username}')
            self.session.headers['__sdcfduid'] = response.cookies['__sdcfduid']
            return
        self.logger.debug(f'\n\tAuthorization: Error: Invalid_token')
        raise AuthorizationtError

    async def __update_invite_id(self) -> None:
        self.__invite_id = self.__invite_link
        if not self.__invite_link.startswith(('https://discord.com/invite/', 'https://discord.gg')):
            raise InviteLinkError(text='Invite link myst be like https://discord.com/invite/34ghH6')
        self.__invite_id = self.__invite_link.split('/')[-1]

    async def __get_xcontext_properties(self) -> None:
        params = {
            "url": f'https://discord.com/api/v7/invites/{self.__invite_id}',
        }
        response: 'requests.Response' = await self._send_request(params)
        try:
            data = json.loads(response.text)
        except Exception as err:
            raise JoinerBaseException(text=str(err))
        location_guild_id = data['guild']['id']
        location_channel_id = data['channel']['id']

        base64_encode_data = b64encode(bytes(
            '{"location":"Accept Invite Page","location_guild_id":"'
            + str(location_guild_id)
            + '","location_channel_id":"'
            + str(location_channel_id)
            + '","location_channel_type":0}', 'utf-8'
        )).decode('utf-8')

        self.session.headers['x-context-properties'] = base64_encode_data
        self.logger.debug("\n\tx-context-properties: OK")

    async def __join(self) -> None:
        params = {
            "url": f'https://discord.com/api/v7/invites/{self.__invite_id}',
            "json": {},
            "verify": False
        }
        response: 'requests.Response' = await self._send_request(params, request_type="post")
        if not response:
            self.logger.debug(f'\n\tJoin: [@{self.__discord_username}] Ошибка No response')
            raise JoiningError(text='No response')
        if response.status_code != 200:
            if json.loads(response.text)['code'] == 40007:
                self.logger.debug(f'\n\tJoin: [@{self.__discord_username}] Ошибка при входе на канал, вы забанены на канале')
                raise JoiningError(text='Ошибка при входе на канал, вы забанены на канале')
            self.logger.debug(f'\n\tJoin: [@{self.__discord_username}] Ошибка при входе на канал, ответ: {response.text}')
            raise JoiningError(text=f'Ошибка при входе на канал, ответ: {response.text}')
        channel_name = json.loads(response.text)['guild']['name']
        channel_id = json.loads(response.text)['guild']['id']
        text = (
            f'\n\tJoin: @{self.__discord_username} успешно вступил в канал {channel_name}'
            f'\n\tServer id: {channel_id}')
        self.logger.debug(text)

    async def __get_xsuperproperties(self) -> None:
        browser_version = str(self._user_agent.split('Chrome/')[-1].split(' ')[0])
        self.__locale = random.choice(['za', 'et', 'ae', 'bh', 'dz', 'eg', 'iq', 'jo', 'kw', 'lb',
                                       'ly', 'ma',
                                       'cl', 'om', 'qa', 'sa', 'sd', 'sy', 'tn', 'ye', 'in', 'az',
                                       'ru', 'by',
                                       'bg', 'bd', 'in', 'cn', 'fr', 'es', 'fr', 'cz', 'gb', 'dk',
                                       'at', 'ch',
                                       'de', 'li', 'lu', 'de', 'mv', 'cy', 'gr', '029', 'au', 'bz',
                                       'ca', 'cb',
                                       'gb', 'ie', 'in', 'jm', 'mt', 'my', 'nz', 'ph', 'sg', 'tt',
                                       'us', 'za',
                                       'zw', 'ar', 'bo', 'cl', 'co', 'cr', 'do', 'ec', 'es', 'gt',
                                       'hn', 'mx',
                                       'ni', 'pa', 'pe', 'pr', 'py', 'sv', 'us', 'uy', 've', 'ee',
                                       'es', 'ir',
                                       'fi', 'ph', 'fo', 'be', 'ca', 'ch', 'fr', 'lu', 'mc', 'nl',
                                       'ie', 'gb',
                                       'ie', 'es', 'fr', 'in', 'il', 'in', 'ba', 'hr', 'de', 'hu',
                                       'am', 'id',
                                       'ng', 'cn', 'id', 'is', 'ch', 'it', 'il', 'jp', 'ge', 'kz',
                                       'gl', 'kh',
                                       'in', 'in', 'kr', 'kg', 'lu', 'la', 'lt', 'lv', 'nz', 'mk',
                                       'in', 'mn',
                                       'ca', 'in', 'bn', 'my', 'mt', 'no', 'np', 'be', 'nl', 'no',
                                       'no', 'za',
                                       'fr', 'in', 'in', 'pl', 'af', 'af', 'br', 'pt', 'gt', 'bo',
                                       'ec', 'pe',
                                       'ch', 'mo', 'ro', 'mo', 'ru', 'rw', 'ru', 'in', 'fi', 'no',
                                       'se', 'lk',
                                       'sk', 'si', 'no', 'se', 'no', 'se', 'fi', 'fi', 'al', 'ba',
                                       'cs', 'me',
                                       'rs', 'sp', 'fi', 'se', 'ke', 'sy', 'in', 'in', 'th', 'tm',
                                       'qs', 'za',
                                       'tr', 'ru', 'cn', 'ua', 'pk', 'uz', 'vn', 'sn', 'za', 'ng',
                                       'cn', 'hk',
                                       'mo', 'sg', 'tw', 'za'])
        xsuperproperties = ''.join((
            '{"os":"Windows","browser":"Chrome","device":"","system_locale":"',
            self.__locale,
            '","browser_user_agent":"',
            self._user_agent,
            '","browser_version":"',
            browser_version,
            '","os_version":"',
            str(random.choice(['7', '10', 'xp', 'vista', '11'])),
            (
                '","referrer":"https://www.yandex.ru/clck/jsredir?from=yandex.ru;suggest;browser&text=",'
                '"referring_domain":"www.yandex.ru",'
                '"referrer_current":"https://www.yandex.ru/clck/jsredir?from=yandex.ru;suggest;browser&text=",'
                '"referring_domain_current":"www.yandex.ru","release_channel":"stable","client_build_number":'
            ),
            str(random.randint(100000, 199999)),
            ',"client_event_source":null}'
        ))
        self.__xsuperproperties: bytes = b64encode(str(xsuperproperties).encode('utf-8'))

    async def _send_request(self, params: dict, request_type: str = "GET") -> 'requests.Response':
        await asyncio.sleep(self.delay)
        response = self.session.request(method=request_type, **params)
        if 'retry_after' in response.text:
            sleep_time = float(json.loads(response.text)['retry_after'])
            text = f'Cooldown, sleeping for {sleep_time} seconds.'
            self.logger.debug(text)
            raise JoinerBaseException(text=text)
        elif 'You need to verify your account in order to perform this action.' in response.text:
            raise JoinerBaseException(
                text='You need to verify your account in order to perform this action.')
        elif 'captcha_sitekey' in response.text:
            for _ in range(2):
                response: requests.Response = await self.__captcha_resolve(
                    response=response, params=params, request_type=request_type)
                self.logger.success(response.text)
                if 'captcha_sitekey' not in response.text:
                    return response
            raise JoinerBaseException(text='Captcha error')
        if response.status_code not in range(200, 300):
            self.logger.error(response.text)

        return response

    async def __captcha_resolve(
            self, response: requests.Response, params: dict, request_type: str
    ) -> requests.Response:
        data: dict = response.json()
        captcha_sitekey: str = data['captcha_sitekey']
        captcha_rqtoken: str = data.get('captcha_rqtoken', '')
        captcha_rqdata: str = data.get('captcha_rqdata', '')
        captcha_key: str = await self._get_anticaptcha(captcha_sitekey, captcha_rqdata)
        params['json'].update({'captcha_key': captcha_key})
        if captcha_rqtoken:
            params['json'].update({'captcha_rqtoken': captcha_rqtoken})

        return self.session.request(method=request_type, **params)

    async def join(self) -> Dict[str, str]:
        """Add user with token to server by invite link

        :returns: dict {'success': True, 'token': token} if done
        else {'success': False, 'token': token, 'message': ...}
        """

        self.logger.debug(f'TOKEN: {self.token}:')
        result = {'success': False, 'token': self.token}
        try:
            await self.__update_invite_id()
            await self._update_proxy()
            await self.__get_xsuperproperties()
            await self.__get_headers()
            await self.__get_finger_print()
            await self.__authorization()
            await self.__get_xcontext_properties()
            await self.__join()
            result.update(success=True)
        except JoinerBaseException as err:
            message = err.text
            self.logger.error(message)
            result.update(message=message)
        except Exception as err:
            self.logger.error(err)
            result.update(message=str(err))

        self.session.close()
        return result

    async def _get_anticaptcha(self, website_key: str, captcha_rqdata: str = '') -> str:
        if not self.anticaptcha_key:
            text = "No anticaptcha key"
            raise CaptchaAPIkeyError(text)
        if not self._proxy:
            text = "No proxy"
            raise CaptchaAPIkeyError(text)
        solver = hCaptchaProxyon()
        solver.set_verbose(1)
        solver.set_key(self.anticaptcha_key)
        if captcha_rqdata:
            solver.set_enterprise_payload({
                "rqdata": captcha_rqdata,
            })
        solver.set_website_url('https://discord.com')
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
