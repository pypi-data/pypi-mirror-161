import requests_cache

from .base import RequestsBase



class CachedRequests(RequestsBase):
    cached_session_params = ['key_fn', 'ignored_parameters', 'match_headers', 'stale_if_error', 'filter_fn']

    def load_session(self):
        return self.apply_settings(
            requests_cache.CachedSession,
            prefix='REQUEST_CACHE_',
            allowed_params=self.cached_session_params
        )
    
    def delete_cache(self, **requests_kwargs):
        key = self.session.cache.create_key(**requests_kwargs)
        self.session.cache.delete(key)

    def fetch(self, *args, **kwargs):
        requests_kwargs = {
            k:v for k, v in kwargs.items()
            if k in self.request_params
        }
        if kwargs.get('refresh') is True:
            self.delete_cache(**requests_kwargs)
        return super().fetch(*args, **kwargs)


