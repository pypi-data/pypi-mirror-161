from distutils.version import LooseVersion

__hooking_module__ = 'pymysql'
__minimum_python_version__ = LooseVersion("2.7")


def safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def connection_info(*args, **kwargs):
    host = safe_get(args, 0) or kwargs.get('host')
    port = safe_get(args, 4) or kwargs.get('port') or 3306
    database = safe_get(args, 3) or \
        kwargs.get('database') or kwargs.get('db')
    return host, port, database


def hook(pymysql):
    from jennifer.wrap import db_api
    db_api.register_database(pymysql, connection_info)
