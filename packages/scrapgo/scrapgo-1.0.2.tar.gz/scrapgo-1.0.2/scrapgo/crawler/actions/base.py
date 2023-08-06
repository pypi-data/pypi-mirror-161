from glob import glob
from dataclasses import dataclass



@dataclass
class BaseAction:
    name:str
    parser:... = None
    extractor:... = None
    refresh:bool = False
    delay:int = None

    def __post_init__(self, *args, **kwargs):
        if not self.name:
            raise NotImplementedError("action name must be specified")

    def as_kwargs(self):
        return self.__dict__


@dataclass
class HttpAction(BaseAction):
    headers:dict=None
    cookies:dict=None
    referer:str=None
    payloader:...=None
    urlfilter:...=None
    fields:list=None
    method:str=None



@dataclass
class UrlRenderAction(HttpAction):
    url:str = None
    urlrenderer:... = None

    def __post_init__(self, *args, **kwargs):
        if not (self.url or self.urlrenderer):
            raise NotImplementedError("an url or urlrenderer must be specified")
    


@dataclass
class UrlPatternAction(HttpAction):
    urlpattern:str=None
    urlpattern_renderer:...=None
    remove_duplicates:bool=None
    attrs:dict=None
    css_selector:str=None
    recursive:bool=False

    def __post_init__(self, *args, **kwargs):
        if not (self.urlpattern or self.urlpattern_renderer):
            raise NotImplementedError("urlpattern or urlpattern_renderer must be specified")


@dataclass
class FileAction(BaseAction):
    path:str=None
    path_renderer:...=None
    method:str='get'

    def __post_init__(self):
        if not (self.path or self.path_renderer):
            raise NotImplementedError("path or path_renderer must be specified")
        self._check_globpath()

    def _check_globpath(self):
        if '*' in self.path:
            self.path_renderer = self.path_renderer or (lambda: glob(self.path, recursive=True))



@dataclass
class CurlAction(BaseAction):
    command:str=None
    command_renderer:...=None

    def __post_init__(self):
        if not (self.command or self.command_renderer):
            raise NotImplementedError("command or command_renderer must be specified")



def urlrender(
    url:str=None, 
    urlrenderer:...=None,
    fields:list=None,
    payloader:...=None,
    parser:...=None,
    extractor:...=None,
    urlfilter:...=None,
    headers:dict=None, referer:str=None, cookies:dict=None,
    method:str=None,
    refresh:bool=False, delay:int=None,
    name:str=None):

    return UrlRenderAction(**locals())

def urlpattern(
    urlpattern:str=None,
    urlpattern_renderer:...=None,
    fields:list=None,
    payloader:...=None,
    parser:...=None,
    extractor:...=None,
    urlfilter:...=None,
    remove_duplicates:bool=None,
    attrs:dict=None,
    css_selector:str=None,
    recursive:bool=False,
    headers:dict=None, referer:str=None, cookies:dict=None, method:str=None,
    refresh:bool=False, delay:int=None,
    name:str=None):
    return UrlPatternAction(**locals())


def curl(
    command:str=None,
    command_renderer:...=None,
    parser:...=None, extractor:...=None,
    refresh:bool=False, delay:int=None,
    name:str=None):
    return CurlAction(**locals())


def file(
    path:str=None,
    path_renderer:...=None,
    parser:...=None,
    extractor:...=None,
    refresh:bool=False,
    delay:int=None,
    name:str=None):
    return FileAction(**locals())
