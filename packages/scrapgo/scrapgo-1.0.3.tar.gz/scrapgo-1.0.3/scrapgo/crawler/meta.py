from collections import abc
from scrapgo.lib import parse_query, extgroup
from dataclasses import dataclass, field

from .actions import UrlPatternAction, UrlRenderAction


@dataclass
class ResponseMeta:
    match:callable = None
    pattern:str = None
    query:dict = None
    soup:... = None
    responsemap:dict = field(default_factory=dict)


    def set_urlutils(self, link, action):
        if isinstance(action, UrlRenderAction):
            if isinstance(link, str):
                self.query = parse_query(link)
            elif isinstance(link, abc.Mapping):
                self.query = link
            else:
                self.query = None
        
        elif isinstance(action, UrlPatternAction):
            self.match = extgroup(action.urlpattern, link)
            self.query = parse_query(link)
    
    def set_responsemap(self, response, action):
        self.responsemap = {
            action.name: response
        }
    
    def update_responsemap(self, prev_response_meta):
        self.responsemap.update(
            prev_response_meta
        )