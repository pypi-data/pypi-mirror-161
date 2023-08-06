import requests
from requests.structures import CaseInsensitiveDict

from scrapgo.settings import FromSettings
from scrapgo.lib import gen_random_value, get_rotate

from .utils import trace, retry_for_raise, rotate_proxy, set_user_agent



class RequestParamsMixin:
    HEADERS = None
    COOKIES = None
    PROXIES = None

    def init_parmas(self):
        self.headers = CaseInsensitiveDict(self.HEADERS)
        self.cookies = self.COOKIES or {}
        self.proxies = self.PROXIES or []
        if hasattr(self, 'settings'):
            if proxy := self.settings.get('REQUESTS_PROXY'):
                self.proxies.append(proxy)

        self.set_user_agent()

    def set_user_agent(self):
        self.apply_settings(
            set_user_agent, self.headers, prefix='FAKE_USER_AGENT_'
        )

    def get_headers(self) -> CaseInsensitiveDict:
        return CaseInsensitiveDict(self.headers)

    def set_header(self, headers:dict):
        self.headers = CaseInsensitiveDict(headers)
    
    def get_cookies(self):
        return dict(self.cookies)
    
    def set_cookies(self, cookies):
        self.cookies = cookies

    def get_first_proxy(self):
        for proxy in self.proxies:
            return proxy

    def rotate_proxies(self):
        if self.proxies:
            self.proxies = get_rotate(self.proxies)
            return self.proxies[0]



class RequestsBase(RequestParamsMixin, FromSettings):
    request_params = ['method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout', 'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json']

    def __init__(self, settings=None):
        super().__init__(settings=settings)
        self.init_parmas()
        self.session = self.load_session()
    
    def get_delay(self, delay=None):
        if delay is not None:
            return delay
        return gen_random_value(*self.settings['REQUEST_DELAY'])

    def load_session(self):
        return requests.Session()

    @trace
    @retry_for_raise
    @rotate_proxy
    def fetch(self, *args, **kwargs):

        response = self.apply_settings(
            self.session.request, prefix='REQUESTS_', 
            *args, **kwargs,
            allowed_params=self.request_params,
        )

        if response.status_code not in self.settings.get('ALLOWABLE_ERROR_STATUS_CODES', []):
            response.raise_for_status()
        return response

