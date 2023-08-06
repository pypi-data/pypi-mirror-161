import time
from distutils.version import LooseVersion

__hooking_module__ = 'asyncio'
__minimum_python_version__ = LooseVersion("3.6")


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def hook(asyncio_module):
    try:
        pass
    except Exception as e:
        print('jennifer.exception', __hooking_module__, 'hook', e)