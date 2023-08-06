import sys
from jennifer.agent import jennifer_agent
from distutils.version import LooseVersion

__hooking_module__ = 'urllib'
__minimum_python_version__ = LooseVersion("2.7")


def wrap_urlopen(urlopen):
    agent = jennifer_agent()

    def handler(*args, **kwargs):
        HTTPResponse = None
        transaction = None
        url = None

        try:
            from urllib import parse
            from urllib.request import Request
            from http.client import HTTPResponse
            transaction = agent.current_transaction()
            url = kwargs.get('url') or args[0]
            if isinstance(url, Request):
                url = url.full_url
            if transaction is not None:
                o = parse.urlparse(url)
                transaction.profiler.external_call(
                    protocol=o.scheme,
                    host=o.hostname,
                    port=o.port or 80,
                    url=url,
                    caller='urllib.request.urlopen',
                )
        except:
            pass

        ret = urlopen(*args, **kwargs)

        try:
            if isinstance(ret, HTTPResponse):
                v = ret.version
                version = 'HTTP/1.1'
                if v == 10:
                    version = 'HTTP/1.0'
                transaction.profiler.end(
                    message='urllib.request.urlopen(url=%s,response=%s,%s)' % (
                        url, version, ret.status)
                )
            else:
                transaction.profiler.end()
        except:
            pass

        return ret
    return handler


def hook(urllib):
    if not sys.version_info.major == 3:
        return

    import urllib.request
    urllib.request.urlopen = wrap_urlopen(urllib.request.urlopen)

