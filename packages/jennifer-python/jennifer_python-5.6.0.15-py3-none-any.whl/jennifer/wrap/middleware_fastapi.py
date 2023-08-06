import base64

from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
import jennifer.agent.agent
import secrets
import time
import struct
import os
from email.utils import formatdate

REQUEST_CTX_ID_KEY = "request_ctx_id"

wmonid_pack = struct.Struct('>Q')
_request_ctx_id = ContextVar(REQUEST_CTX_ID_KEY, default=None)


def get_request_ctx_id():
    ctx_value = _request_ctx_id.get()
    return ctx_value

# fastapi requires Python 3.6
class APMMiddleware(BaseHTTPMiddleware):
    _agent = jennifer.agent.jennifer_agent()
    jennifer.agent.agent.Agent.set_context_id_func(_agent, get_request_ctx_id)

    # def __init__(self, app):
    #     pass

    @staticmethod
    def get_wmonid(request):
        wmon_id_value = None
        wmon_id_encoded = None

        cookie_wmonid = request.cookies.get('WMONID')
        if cookie_wmonid is not None:
            try:
                wmon_id_encoded = cookie_wmonid
                wmon_id_value, = wmonid_pack.unpack(base64.b64decode(wmon_id_encoded))
            except Exception as e:
                print(e)

        if wmon_id_value is None:
            wmon_id_value = (os.getpid() << 32) + int(time.time())
            wmon_id_encoded = wmonid_pack.pack(wmon_id_value)

        return wmon_id_value, wmon_id_encoded, cookie_wmonid is not None

    @staticmethod
    def set_wmonid(response, wmon_id_value, cookie_exists_wmonid):
        if cookie_exists_wmonid:
            return

        expire = formatdate(timeval=time.time() + 31536000, localtime=False, usegmt=True)
        response.set_cookie('WMONID', base64.b64encode(wmon_id_value).decode('ascii'), expires=expire, max_age=31536000)

    async def dispatch(self, request, call_next):
        transaction = None
        cookie_exists_wmonid = False

        try:
            request_id = _request_ctx_id.set(int.from_bytes(secrets.token_bytes(4), "big"))
            wmonid, wmonid_encoded, cookie_exists_wmonid = self.get_wmonid(request)

            transaction = APMMiddleware._agent.start_transaction(request.headers, wmonid, path_info = request.url.path)

            if transaction is not None:
                profiler = transaction.profiler

                if profiler is not None:
                    profiler.set_root_name("fastapi.dispatch")
                    profiler.message('request url == %s' % str(request.url))
        except:
            jennifer.agent.log_ex('APMMiddleware.dispatch.pre')

        response = await call_next(request)

        try:
            self.set_wmonid(response, wmonid_encoded, cookie_exists_wmonid)

            if transaction is not None:
                end_time = APMMiddleware._agent.current_time()
                transaction.end_of_profile(end_time)

            _request_ctx_id.reset(request_id)
        except:
            jennifer.agent.log_ex('APMMiddleware.dispatch.post')

        return response
