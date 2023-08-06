import os
import http
import warnings
import json
import yaml
import logging
import logging.config
import ecs_logging

from http import client
from functools import partial
from typing import Union
from fasal_logger._logger import SlackNotification, FasalStdlibFormatter

class LoggerInitializer():
    def __call__(self, logger, config):
        config = os.path.abspath(config)
        self._configure(config)
        http.client.HTTPConnection.debuglevel = 1
        http_print = partial(self._print_to_log, logger)
        http.client.print = http_print

    def _configure(self, config):
        if not os.path.exists(config):
            raise FileNotFoundError(f"Check if the .yml file is present in this path or not ({config})")
        with open(config, 'r') as f:
            _config = yaml.safe_load(f.read())
            _config = self._expand_vars(_config)
            logging.config.dictConfig(_config)

    def _expand_vars(self, config_var) -> Union[dict, str]:
        def expand(config_var) -> str:
            if isinstance(config_var, str):
                config_var = os.path.expandvars(config_var)
                if '$' in config_var:
                    warnings.warn("environment variable parsing failed", stacklevel=2)
            return config_var
        config = expand(config_var)
        if isinstance(config_var, dict):
            _config_var = json.dumps(config_var)
            config_var = json.loads(expand(_config_var))

        return config_var

    def _print_to_log(self, logger, *args, **kwargs):
        k = ".".join(args[:-1])
        v = args[-1]
        extra = ecs_logging._utils.de_dot(k,v)
        extra.update(kwargs)
        extra.update({'type': 'access-log'})
        logger.debug("HTTP log", extra=extra)


