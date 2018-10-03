# coding: UTF-8

from pprint import pprint

import logging
import logging.config
import inspect
import os

script_path = os.path.dirname(os.path.abspath(inspect.currentframe().f_code.co_filename))
logging.config.fileConfig(script_path + '/../logger.conf', disable_existing_loggers=True)
logger = logging.getLogger('mylogger')

# Ruby's Hash#dig like function
# https://utgwkk.hateblo.jp/entry/2016/11/14/144209#fn-24c52eaa
def dig(obj, *keys, error=False, none_value=""):
    keys = list(keys)
    if isinstance(keys[0], list):
        return dig(obj, *keys[0], error=error)

    if isinstance(obj, dict) and keys[0] in obj or \
       isinstance(obj, list) and keys[0] < len(obj):
        if len(keys) == 1:
            return obj[keys[0]]
        return dig(obj[keys[0]], *keys[1:], error=error)

    if keys[0] in obj:
        if len(keys) == 1:
            return obj[keys[0]]
        return dig(obj[keys[0]], *keys[1:], error=error)

    if error:
        raise KeyError(keys[0])

    return none_value
