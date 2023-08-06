from pathlib import Path
from collections import abc

from scrapgo.lib import queryjoin, urljoin
from .base import UrlRenderAction,  FileAction, CurlAction



def resolve_link(action, link, response=None):
    if isinstance(action, FileAction):
        if link.startswith('file:///'):
            return link
        else:
            return Path(link).absolute().as_uri()
            
    if isinstance(action, CurlAction):
        return link

    if isinstance(action, UrlRenderAction): 
        host = action.url or response.url
    else:
        host = response.url

    if isinstance(link, abc.Mapping):
        return queryjoin(host, link)
    return urljoin(host, link)
