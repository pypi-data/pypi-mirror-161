from distutils.version import LooseVersion

__hooking_module__ = 'sqlite3'
__minimum_python_version__ = LooseVersion("2.7")


def connection_info(database, *args, **kwargs):
    return 'localhost', 0, database


def hook(sqlite3):
    from jennifer.wrap import db_api
    db_api.register_database(sqlite3, connection_info)

    if sqlite3.dbapi2 is not None:
        db_api.register_database(sqlite3.dbapi2, connection_info)
