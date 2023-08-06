import os
from FConvert import CONVERT

def get_os_variable(varName, default=False, toBool=False):
    try:
        raw = os.environ[varName]
        if toBool:
            c = CONVERT.TO_bool(raw)
            return c
        return raw
    except:
        return default