import functools, time

from requests.exceptions import ProxyError, ConnectTimeout
from fake_useragent import FakeUserAgent

from scrapgo.lib import format_bytes_size
from .exceptions import *



def set_user_agent(header, agent_name, **fkagent_kwargs):
    fagent = FakeUserAgent(**fkagent_kwargs)
    if 'user-agent' not in map(str.lower, header):
        header['User-Agent'] = getattr(fagent, agent_name)


def as_reqeusts_kwargs(**kwargs):
    params = ['method', 'url', 'params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout', 'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json']
    return {
        k:v for k, v in kwargs.items()
        if k in params
    }


def _get_pre_request_log(method, url, data=None, proxies=None, **extra):
    METHOD = method.upper()
    PROXIES = f"proxy:{proxies}" if proxies else '' 
    prefix = ' '.join(filter(None, [METHOD, url, PROXIES]))
    PAYLOADS = f"payloads:{format_bytes_size(payloads, 2)}" if (data:=data) and (payloads := len(data)) else ''
    
    if postfix:= list(filter(None, [PAYLOADS])):
        postfix = ', '.join(postfix)
        postfix = f' ({postfix})'
    else:
        postfix = ''

    log = f"{prefix}{postfix}"
    return log

def _get_after_request_log(response, delay):
    content_length = len(response.content or '')
    status = response.status_code
    reason = response.reason
    size_exp = format_bytes_size(content_length)
    elapsed = round(response.elapsed.microseconds / (1000 * 1000),2)

    log = f'{status} {reason} {size_exp} {elapsed}s'

    if ctype:= response.headers.get('Content-Type'):
        log = f'{log} {ctype}'

    if hasattr(response, 'from_cache'):
        if response.from_cache:
            log = f'{log} (From Cache)'
            return log
    
    log = f'{log} (delay:{delay or 0}s)'
    return log


def trace(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        delay = self.get_delay(kwargs.get('delay'))
        try:
            proxy = self.get_first_proxy()
            pre_log = _get_pre_request_log(proxies=proxy, **kwargs)
            if self.settings['REQUEST_LOGGING']:
                print(f'{pre_log}')
            r = func(self, *args, **kwargs)
        except Exception as e:
            print(e)
            raise
        else:
            log = f'  => {_get_after_request_log(r, delay)}'
            if self.settings['REQUEST_LOGGING']:
                print(log)
            if hasattr(r, 'from_cache'):
                if r.from_cache:
                    return r
            time.sleep(delay)
            return r
    return wrapper



def retry_for_raise(fetch):
    @functools.wraps(fetch)
    def wrapper(self, *args, **kwargs):
        url = kwargs.get('url')
        retry_intervals = list(self.settings['RETRY_INTERVAL_SECONDS'])
        while retry_intervals:
            try:
                response = fetch(self, *args, **kwargs)
            except Exception as e:
                if self.proxies and isinstance(e, RotateProxiesDone):
                    raise
                interval = retry_intervals.pop(0)
                print(f" - {e}")
                print(f" - Request {url} Failed, retry after {interval} sec...(retry remains: {len(retry_intervals)})")
                time.sleep(interval)
            else:
                return response
        raise RetryMaxCountDone(f"Request for {url} has failed!")
    return wrapper


def rotate_proxy(fetch):
    @functools.wraps(fetch)
    def wrapper(self, *args, **kwargs):
        proxy = self.get_first_proxy()
        if not proxy or kwargs.get('proxies'):
            return fetch(self, *args, **kwargs)

        kwargs.update({'proxies': proxy})

        rotate_count = 0
        while True:
            try:
                response = fetch(self, *args, **kwargs)
            except (ProxyError, ConnectTimeout) as e:
                next_proxy = self.rotate_proxies()
                rotate_count += 1

                if proxy == next_proxy:
                    raise RotateProxiesDone("All requests through {len(self.proxies)} proxies fail")
    
                kwargs.update({'proxies': next_proxy})
                print(f" - The requests by pass proxy server {proxy} has failed. Trying to next proxy server {next_proxy}...(rotate rate: {rotate_count}/{len(self.proxies)})")
            else:
                return response
    return wrapper
