import sys
from jennifer.agent import jennifer_agent
from distutils.version import LooseVersion

__hooking_module__ = 'requests'
__minimum_python_version__ = LooseVersion("2.7")


global parse_url_func


def parse_url2(url):
    from urlparse import urlparse
    return urlparse(url)


def parse_url3(url):
    from urllib import parse
    return parse.urlparse(url)


def wrap_send(origin):
    agent = jennifer_agent()
    global parse_url_func

    if sys.version_info.major == 3:
        parse_url_func = parse_url3
    else:
        parse_url_func = parse_url2

    def handler(self, request, **kwargs):
        transaction = None
        url = None
        try:
            transaction = agent.current_transaction()
            url = request.url

            if transaction is not None:
                o = parse_url_func(url)
                transaction.profiler.external_call(
                    protocol=o.scheme,
                    host=o.hostname,
                    port=o.port or 80,
                    url=url,
                    caller='requests.Session.send',
                )
        except:
            pass

        ret = origin(self, request, **kwargs)

        try:
            if transaction is not None:
                message = None
                if ret is not None:
                    message = 'requests.Session.send(url=%s,response=%s)' % (url, ret.status_code)
                transaction.profiler.end(message=message)
        except:
            pass

        return ret

    return handler


def hook(requests):
    requests.Session.send = wrap_send(requests.Session.send)
