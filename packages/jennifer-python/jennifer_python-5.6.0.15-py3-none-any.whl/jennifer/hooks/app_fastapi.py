import time
from distutils.version import LooseVersion

__hooking_module__ = 'fastapi'
__minimum_python_version__ = LooseVersion("3.6")


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def hook(fastapi_module):
    try:
        fastapi_module.FastAPI = _wrap_fastapi(fastapi_module.FastAPI)
        fastapi_module.concurrency.run_in_threadpool = _wrap_run_in_threadpool(fastapi_module.concurrency.run_in_threadpool)
    except Exception as e:
        print('jennifer.exception', __hooking_module__, 'hook', e)


def _wrap_fastapi(origin_fastapi):
    from jennifer.wrap import middleware_fastapi

    def _handler(*args, **kwargs):
        app = origin_fastapi(*args, **kwargs)
        app.add_middleware(middleware_fastapi.APMMiddleware)
        return app

    return _handler


def _wrap_run_in_threadpool(origin_run_in_threadpool):
    from jennifer.agent import jennifer_agent
    agent = jennifer_agent()

    async def _handler(*args, **kwargs):
        transaction = None

        try:
            func = _safe_get(args, 0) or kwargs.get('func') or None
            transaction = agent.current_transaction()

            if transaction is not None:
                transaction.profiler.method("run_in_threadpool." + func.__name__)
        except:
            agent.log_ex('run_in_threadpool.pre')

        return_value = await origin_run_in_threadpool(*args, **kwargs)

        try:
            if transaction is not None:
                transaction.profiler.end()
        except:
            agent.log_ex('run_in_threadpool.post')

        return return_value

    return _handler
