from collections import abc
from bs4 import BeautifulSoup, element

from scrapgo.lib import strcompile, prettier, is_many_type
from scrapgo.settings import FromSettings

from .exceptions import *



class SoupParser(FromSettings):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _load_soup(self, content):
        soup = self.apply_settings(BeautifulSoup, content, prefix='BS4_')
        return soup

    def _is_parsable(self, response):
        content_type_info = response.headers.get('Content-Type')
        if not content_type_info:
            return False

        for ctype in self.settings['PARSE_CONTENT_TYPES']:
            if ctype in content_type_info:
                return True
        return False
    
    def parse_linkpattern(self, content, urlpattern, remove_duplicates=True, attrs=None, css_selector=None, **kwargs):
        soup = self._load_soup(content)
        if css_selector:
            soup = soup.select_one(css_selector) or soup

        compiled = strcompile(urlpattern)

        parsed = [
            sp[attr].strip()
            for attr in attrs or self.settings['CRAWL_TARGET_ATTRS']
            for sp in soup(attrs={attr: compiled})
        ]

        if remove_duplicates:
            parsed = list(dict.fromkeys(parsed))
        return parsed
    
    def validate_extracted(self, extracted, func, meta, _root=True):
        
        if not isinstance(meta.soup, BeautifulSoup):
            raise CannotExtractError(f"{func.__name__} won't recive soup instance or None")
 
        if isinstance(extracted, element.Tag):
            if self.settings['EXTRACT_AUTO_SOUP2TEXT']:
                extracted = extracted.get_text(strip=self.settings['EXTRACT_AUTO_STRIP'])
            if self.settings['EXTRACT_AUTO_PRETTIFY']:
                extracted = prettier(extracted)
        elif isinstance(extracted, str):
            if self.settings['EXTRACT_AUTO_STRIP']:
                extracted = extracted.strip()
            if self.settings['EXTRACT_AUTO_PRETTIFY']:
                extracted = prettier(extracted)
        elif isinstance(extracted, abc.Mapping):
            ext = extracted.__class__()
            for key, val in extracted.items():
                val = self.validate_extracted(val, func, meta, _root=False)
                if self.settings['EXTRACT_AUTO_PRETTIFY']:
                    key = prettier(key)
                ext[key] = val
            return ext
        elif is_many_type(extracted):
            extracted_list = [
                self.validate_extracted(ext, func, meta, _root=False) for ext in extracted
            ]
            return extracted_list
        return extracted
