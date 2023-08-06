from ..lib.module import reduce_module2dict, select_kwargs
from . import base



class FromSettings:

    def __init__(self, settings=None):
        self.settings = reduce_module2dict(base)
        if settings:
            self.settings.update(reduce_module2dict(settings))
            self.settings = self.valid_settings(self.settings)

    def valid_settings(self, settings):
        self._validate_request_delay(settings)
        self._validate_retry_interval_seconds(settings)
        return settings

    def apply_settings(self, callable, *args, prefix:str=None, lowerkey:bool=True, allowed_params:list=None, **kwargs):
        if prefix:
            settings_kwargs = {
                k.replace(prefix, ''): v for k, v in self.settings.items()
                if k.startswith(prefix)
            }
        else:
            settings_kwargs = dict(self.settings)
            
        if lowerkey:
            settings_kwargs = {
                k.lower(): v for k,v in settings_kwargs.items()
            }
        updated_params = {**settings_kwargs, **kwargs}
        return select_kwargs(callable, *args, allowed_params=allowed_params, **updated_params)


    def _validate_retry_interval_seconds(self, settings):
        value = settings['RETRY_INTERVAL_SECONDS']
        if value is None:
            value = ()

        if isinstance(value, (int, float)):
            value = value, 
        
        if not isinstance(value, (tuple, list)):
            raise ValueError('RETRY_INTERVAL_SECONDS must be tuple of numbers or a number')
        settings['RETRY_INTERVAL_SECONDS'] = value


    def _validate_request_delay(self, settings):
        value = settings['REQUEST_DELAY']
        if not value:
            value = 0, 0
        elif isinstance(value, (int, float)):
            value = value, value,
        elif isinstance(value, (list, tuple)):
            if len(value) == 1:
                value = value[0], value[0]
            else:
                value = value[0], value[-1]
        else:
            raise ValueError('REQUEST_DELAY must be tuple of numbers or a number')
        settings['REQUEST_DELAY'] = value


