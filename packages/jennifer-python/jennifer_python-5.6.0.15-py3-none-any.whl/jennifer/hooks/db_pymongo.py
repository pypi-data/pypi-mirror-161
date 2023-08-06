
from os import getenv
from jennifer.api.proxy import Proxy
from jennifer.agent import jennifer_agent
# from packaging import version
from distutils.version import LooseVersion
import json

__hooking_module__ = 'pymongo'
__minimum_python_version__ = LooseVersion("2.7")


def _debug_log(text):
    if getenv('PY_DBG'):
        log_socket = __import__('jennifer').get_log_socket()
        if log_socket is not None:
            log_socket.log(text)


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


class CollectionProxy(Proxy):
    def __init__(self, obj, host, port, name):
        Proxy.__init__(self, obj)
        self.set('collection', name)
        self.set('host', host)
        self.set('port', port)

    def with_options(self, *args, **kwargs):
        obj = self._origin.with_options(*args, **kwargs)
        return CollectionProxy(obj, self.host, self.port, self.collection)

    def find(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()
            parameter = None
            document = _safe_get(args, 0)
            try:
                parameter = json.dumps(document)
            except:
                parameter = "..."

            if transaction is not None:
                transaction.profiler.db_execute(self.host, self.port, self.collection + '.find(' + parameter + ')')
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.find(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result

    def find_one_and_replace(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()
            parameter = None
            filter_ = _safe_get(args, 0) or kwargs.get('filter')
            replacement = _safe_get(args, 1) or kwargs.get('replacement')

            try:
                parameter = [json.dumps(filter_), json.dumps(replacement)]
            except:
                parameter = "..."

            if transaction is not None:
                transaction.profiler.db_execute(
                    self.host, self.port,
                    self.collection + '.find_one_and_replace(' + parameter[0] + ', ' + parameter[1] + ')')
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.find_one_and_replace(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result

    def insert_many(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()
            parameter = None
            document = _safe_get(args, 0) or kwargs.get('documents')
            try:
                parameter = json.dumps(document)
            except:
                parameter = "..."

            if transaction is not None and parameter is not None:
                transaction.profiler.db_execute(
                    self.host, self.port, self.collection + ".insert_many(" + parameter + ")")
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.insert_many(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result

    def update_many(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()

            filter_expression = _safe_get(args, 0) or kwargs.get('filter')
            update_expression = _safe_get(args, 1) or kwargs.get('update')

            try:
                parameter = json.dumps(filter_expression)
                parameter = parameter + ", " + json.dumps(update_expression)
            except:
                parameter = "..."

            if transaction is not None:
                transaction.profiler.db_execute(
                    self.host, self.port, self.collection + ".update_many(" + parameter + ")")
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.update_many(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result

    def update_one(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()
            filter_expression = _safe_get(args, 0) or kwargs.get('filter')
            update_expression = _safe_get(args, 1) or kwargs.get('update')

            try:
                parameter = json.dumps(filter_expression)
                parameter = parameter + ", " + json.dumps(update_expression)
            except:
                parameter = "..."

            if transaction is not None:
                transaction.profiler.db_execute(
                    self.host, self.port, self.collection + ".update_one(" + parameter + ")")
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.update_one(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result

    def insert_one(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()
            parameter = None
            document = _safe_get(args, 0) or kwargs.get('document')

            try:
                parameter = json.dumps(document)
            except:
                parameter = "..."

            if transaction is not None:
                transaction.profiler.db_execute(self.host, self.port, self.collection + ".insert_one(" + parameter + ")")
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.insert_one(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result

    def delete_many(self, *args, **kwargs):
        transaction = None

        try:
            transaction = jennifer_agent().current_transaction()
            parameter = None
            document = _safe_get(args, 0) or kwargs.get('filter')

            try:
                parameter = json.dumps(document)
            except:
                parameter = "..."

            if transaction is not None:
                transaction.profiler.db_execute(self.host, self.port, self.collection + ".delete_many(" + parameter + ")")
        except:
            pass

        result = None

        try:
            try:
                result = self._origin.delete_many(*args, **kwargs)
            except Exception as e:
                if transaction is not None:
                    transaction.profiler.end()
                    transaction.profiler.sql_error(e)
                raise e

            if transaction is not None:
                transaction.profiler.end()
        except:
            pass

        return result


class DatabaseProxy(Proxy):
    def __init__(self, obj, host, port, name):
        Proxy.__init__(self, obj)
        self.set('db', name)

        origin_getitem = self._origin.__getitem__

        def getitem(key_name):
            collection = origin_getitem(key_name)

            if isinstance(collection, CollectionProxy):
                return collection
            else:
                return CollectionProxy(collection, host, port, self.db + '.' + key_name)

        self._origin.__getitem__ = getitem


def hook(pymongo):
    mongo_client_origin = pymongo.MongoClient

    class MongoClientWrap3(mongo_client_origin):
        def __init__(*args, **kwargs):
            mongo_client_origin.__init__(*args, **kwargs)

        def __getitem__(self, name):
            database = mongo_client_origin.__getitem__(self, name)
            host, port = self.address
            return DatabaseProxy(database, host, port, name)

        def get_database(*args, **kwargs):
            database = mongo_client_origin.get_database(*args, **kwargs)

            myself = _safe_get(args, 0)
            name = _safe_get(args, 1) or kwargs.get('name')

            host, port = myself.address
            return DatabaseProxy(database, host, port, name)

    class MongoClientWrap4(mongo_client_origin):
        def __init__(*args, **kwargs):
            mongo_client_origin.__init__(*args, **kwargs)

            myself = _safe_get(args, 0)
            myself.__host = _safe_get(args, 1) or kwargs.get('host') or '127.0.0.1'
            myself.__port = _safe_get(args, 2) or kwargs.get('port') or 27017

        def __getitem__(self, name):
            database = mongo_client_origin.__getitem__(self, name)
            return DatabaseProxy(database, self.__host, self.__port, name)

        def get_database(*args, **kwargs):
            database = mongo_client_origin.get_database(*args, **kwargs)

            myself = _safe_get(args, 0)
            name = _safe_get(args, 1) or kwargs.get('name')

            return DatabaseProxy(database, myself.__host, myself.__port, name)

    current_ver = LooseVersion(pymongo.__version__)
    base_ver = LooseVersion("3.12.3")
    if current_ver <= base_ver:
        pymongo.MongoClient = MongoClientWrap3
    else:
        pymongo.MongoClient = MongoClientWrap4
