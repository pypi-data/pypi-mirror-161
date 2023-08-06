from collections import deque

from scrapgo.core import SoupParser, RequestsBase, CachedRequests
from scrapgo.core.http import RequestsBase
from scrapgo.lib import is_many_type, pluralize

from .actions import resolve_link, ReduceMixin, UrlPatternAction
from .meta import ResponseMeta



class CrawlMixin(ReduceMixin, SoupParser):
    urlorders = None

    def crawl(self, _response=None, _urlorders=None, _results=None, _responsemap=None, _composed:dict=None):
        
        action, *rest = _urlorders or self.urlorders

        _composed = _composed or dict()
        response_queue = deque([_response])

        if _urlorders == []:
            response_queue = deque()
        
        visited = set()
        while response_queue:
            response = response_queue.pop()
            
            cookies = self.dispatch_cookies(action)
            headers = self.dispatch_headers(action)
            headers.update(self.dispatch_referer(action, response))

            is_parsable = True
            
            for link in self.dispatch_renderer(action, response, _responsemap, _results):
                                
                url = resolve_link(action, link, response)
                url = self.dispatch_fields(action, url)

                if not self.dispatch_urlfilter(action, url, _responsemap, _results):
                    continue
                    
                if isinstance(action, UrlPatternAction):
                    if url in visited:
                        continue
                    visited.add(url)

                #check post method
                for payloads in self.dispatch_payloader(action, _responsemap, _results):
                    requests_kwargs = dict(url=url, headers=headers, cookies=cookies)

                    # if payloads is {}, explicitly to None
                    payloads = payloads or None

                    json_type = False
                    if content_type := headers.get('Content-Type'):
                        if 'application/json' in content_type:
                            json_type = isinstance(payloads, (dict, list))

                    requests_kwargs['json' if json_type else 'data'] = payloads

                    sub_response = self.dispatch_response(action, **requests_kwargs)

                    ## content type check
                    # soup로로 처리 불가능 한것은 content 그대로 넘김
                    soup = sub_response.content
                    is_parsable = self._is_parsable(sub_response)
                    if is_parsable:
                        soup = self._load_soup(soup)

                    ## respone meta setting
                    meta = ResponseMeta(soup=soup)
                    meta.set_urlutils(link, action)
                    meta.set_responsemap(sub_response, action)

                    if response:
                        meta.update_responsemap(response.crawler.responsemap)
                    setattr(sub_response, 'crawler', meta)

                    if _responsemap:
                        meta.update_responsemap(_responsemap)

                    ## parsing
                    extracted = self.dispatch_extractor(action, meta, sub_response, _results, _composed)
                    results = self.dispatch_parser(action, sub_response, extracted, meta, _results, _composed)

                    if is_many_type(results):
                        results = list(results)                    
                    
                    ## results proccessing
                    if hasattr(self, 'compose'):
                        _composed.setdefault(action.name ,[])
                        _composed[action.name] += pluralize(results)

                    if is_parsable is True:
                        if isinstance(action, UrlPatternAction):
                            if action.recursive:
                                response_queue.append(sub_response)
                        self.crawl(sub_response, rest, results, meta.responsemap, _composed)
                        
            # BFO if not passable
            if is_parsable is False:
                self.crawl(response, rest, results or _results, meta.responsemap, _composed)
        
        if _response is None:
            self.dispatch_compose(_composed)
    


class RequestsCrawler(CrawlMixin, RequestsBase):
    pass


class CachedRequestsCrawler(CrawlMixin, CachedRequests):
    pass
