from distutils.version import LooseVersion

__hooking_module__ = 'psycopg2'
__minimum_python_version__ = LooseVersion("2.7")


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def _connection_info(*args, **kwargs):
    host = kwargs.get('host')
    port = kwargs.get('port') or 5432
    database = kwargs.get('dbname')

    try:
        if host is None:
            connection_string = _safe_get(args, 0)
            host, port, database = _get_db_info_from_string(connection_string)
    except:
        pass

    return host, port, database


def _get_db_info_from_string(text):
    key_value = dict(item.split('=') for item in text.split(' '))

    port = 5432
    if key_value['port'] is not None:
        port = int(key_value['port'])

    return key_value['host'], port, key_value['dbname']


def _unwrap_register_type_args(obj, scope=None):
    return obj, scope


def _wrap_register_type(register_type_func):

    def handler(*args, **kwargs):
        try:
            from jennifer.wrap import db_api

            obj, scope = _unwrap_register_type_args(*args, **kwargs)

            if scope and isinstance(scope, db_api.Proxy):
                scope = scope._origin

            return register_type_func(obj, scope)
        except:
            return register_type_func(*args, **kwargs)

    return handler


def hook(psycopg2):
    from jennifer.wrap import db_api
    db_api.register_database(psycopg2, _connection_info)

    psycopg2.extensions.register_type = _wrap_register_type(psycopg2.extensions.register_type)
    psycopg2._psycopg.register_type = _wrap_register_type(psycopg2._psycopg.register_type)

    current_ver = LooseVersion(psycopg2.__version__)
    base_ver = LooseVersion("2.5")

    if current_ver >= base_ver:
        psycopg2._json.register_type = _wrap_register_type(psycopg2._json.register_type)
