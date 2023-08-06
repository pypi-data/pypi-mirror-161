from distutils.version import LooseVersion

__hooking_module__ = 'cx_Oracle'
__minimum_python_version__ = LooseVersion("2.7")


def safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def connection_info(*args, **kwargs):
    try:
        dsn = safe_get(args, 2) or kwargs.get('dsn')

        host, port, service_name = get_host_and_service_name(dsn)
        return host, port, service_name
    except:
        return '(None)', 1521, '(None)'


def get_host_and_service_name(dsn_text):
    found = dsn_text.find('/')
    if found == -1:
        host, port = get_host_and_port(dsn_text)
        return host, port, ''

    host, port = get_host_and_port(dsn_text[:found])
    return host, port, dsn_text[found + 1:]


def get_host_and_port(text):
    found = text.find(':')
    if found == -1:
        return text, 1521

    return text[:found], int(text[found + 1:])


def hook(cs_oracle_db):
    from jennifer.wrap import db_api
    db_api.register_database(cs_oracle_db, connection_info)
