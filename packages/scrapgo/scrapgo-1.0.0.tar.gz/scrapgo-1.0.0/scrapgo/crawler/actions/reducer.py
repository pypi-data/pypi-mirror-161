from urllib.error import URLError

from scrapgo.lib import select_kwargs, filter_params, find_function, curl2requests, assingles
from .base import UrlRenderAction, UrlPatternAction, FileAction, CurlAction
from .exceptions import *



class ReduceMixin:

    def get_action(self, name):
        for action in self.urlorders:
            if action.name == name:
                return action    

    def dispatch_response(self, action, **kwargs):
        if isinstance(action, CurlAction):
            command = kwargs.get('url')
            request_kwargs = curl2requests(command)
            return self.fetch(refresh=action.refresh, delay=action.delay, **request_kwargs)

        method = action.method or ('post' if kwargs.get('data') else 'get')
        return self.fetch(method=method, refresh=action.refresh, delay=action.delay, **kwargs)

    @assingles
    def dispatch_renderer(self, action, response, responsemap, prev_results):
        if isinstance(action, UrlRenderAction):
            if urlrenderer := action.urlrenderer:
                return self.dispatch(
                    'urlrenderer', urlrenderer,
                    url=action.url, parent_response=response, responsemap=responsemap,
                    prev=prev_results
                )                
            return action.url

        elif isinstance(action, UrlPatternAction):
            if urlpattern_renderer := action.urlpattern_renderer:
                urlpattern = self.dispatch(
                    'urlpattern_renderer', urlpattern_renderer,
                    pattern=action.urlpattern, parent_response=response, responsemap=responsemap,
                    prev=prev_results
                )
                if urlpattern is None:
                    raise UrlRendererError(f"{urlpattern_renderer} must return regex pattern of url, not {urlpattern}")
            else:
                urlpattern = action.urlpattern
            kwargs = {
                **action.as_kwargs(),
                'urlpattern': urlpattern
            }
            return self.parse_linkpattern(response.content, **kwargs)
    
        elif isinstance(action, CurlAction):
            if command_renderer:= action.command_renderer:
                return self.dispatch(
                    'curlrenderer', command_renderer,
                    command=action.command, parent_resposne=response, responsemap=responsemap,
                    prev=prev_results
                )
            return action.command
        elif isinstance(action, FileAction):
            if path_renderer := action.path_renderer:
                return self.dispatch(
                    'path_renderer', path_renderer,
                    path=action.path, parent_resposne=response, responsemap=responsemap,
                    prev=prev_results
                )
            return action.path
        else:
            raise CannotFindAction(f'{action} is not memeber of renderer action')

    @assingles
    def dispatch_payloader(self, action, responsemap, prev_results):
        if not hasattr(action, 'payloader') or not action.payloader:
            return {}
        else:
            return self.dispatch(
                'payloader', action.payloader,
                responsemap=responsemap, prev=prev_results
            )
            
    def dispatch_fields(self, action, url):
        if not hasattr(action, 'fields'):
            return url
        url = filter_params(url, action.fields)
        return url

    def dispatch_headers(self, action):
        headers = self.get_headers()
        if hasattr(action, 'headers'):
            headers.update(action.headers or {})
        return headers
    
    def dispatch_cookies(self, action):
        cookies = self.get_cookies()
        if hasattr(action, 'cookies'):
            cookies.update(action.cookies or {})
        return cookies

    def dispatch_extractor(self, action, meta, response, prev_results, results_cache):
        extractset = {}
        if module := action.extractor:
            pat = r'^extract_(?P<ext>\w+)$'
            for g, func in find_function(module, pat):
                extracted = select_kwargs(
                    func,
                    response=response,
                    meta=meta,
                    soup=meta.soup,
                    prev=prev_results,
                    results_set=results_cache
                )
                extractset[g('ext')] = self.validate_extracted(extracted, func, meta)
        return extractset

    def dispatch_parser(self, action, response, extracted, meta, prev_results, results_cache):
        results = self.dispatch(
            'parser', action.parser,
            response=response, parsed=extracted, meta=meta,
            prev=prev_results,
            results_set=results_cache
        )
        return results

    def dispatch_urlfilter(self, action, url, responsemap, prev_results):
        if not hasattr(action, 'urlfilter'):
            return True

        return self.dispatch(
            'urlfilter', action.urlfilter,
            url=url, responsemap=responsemap, prev=prev_results
        )
    
    def dispatch_referer(self, action, response):
        headers = self.get_headers()
        if not hasattr(action, 'referer'):
            return headers
        
        if action.referer and response:
            try:
                referer = response.crawler.responsemap[action.referer]
            except KeyError:
                raise CannotFindAction(f"An action named {action.referer} could not be found at urlorders.")
            else:
                headers['Referer'] = referer.url
        return headers


    def dispatch_compose(self, results_set):
        if hasattr(self, 'compose'):
            composed = self.dispatch(
                'compose', self.compose,
                **results_set
            )
            return composed


    def dispatch(self, type, func, *args, **kwargs):
        if callable(func):
            f = func
        elif isinstance(func, str):
            if hasattr(self, func):
                f = getattr(self, func)
            else:
                raise NotImplementedError(f"The method {func} is not implemented!")
        else:
            f = {
                'urlfilter': self.default_urlfilter,
                'parser': self.default_parser,
                'urlrenderer': self.default_urlrenderer,
                'urlpattern_renderer': self.default_pattern_renderer,
                'breaker': self.default_breaker,
                'payloader': self.default_payloader,
                'curlrenderer': self.default_curlrenderer,
                'path_renderer': self.default_path_renderer,
            }[type]

        return select_kwargs(f, *args, **kwargs)
    

    def default_urlfilter(self, url, **kwargs):
        return True
    
    def default_parser(self, response, **kwargs):
        return
    
    def default_urlrenderer(self, url, response, **kwargs):
        yield url
    
    def default_curlrenderer(self, curl, resposne, **kwargs):
        return curl
    
    def default_path_renderer(self, path, response, **kwargs):        
        return path
        
    def default_pattern_renderer(self, pattern, resposne, **kwargs):
        return pattern
    
    def default_breaker(self, response, **kwargs):
        return False
    
    def default_payloader(self):
        yield
    