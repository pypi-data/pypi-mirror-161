import sys

from jennifer.agent import jennifer_agent
from distutils.version import LooseVersion

__hooking_module__ = 'urllib2'
__minimum_python_version__ = LooseVersion("2.7")

global parse_url_func2


def parse_url2(url):
    from urlparse import urlparse
    return urlparse(url)


def parse_url3(url):
    from urllib import parse
    return parse.urlparse(url)


def wrap_urlopen(urlopen):
    agent = jennifer_agent()
    global parse_url_func2

    if sys.version_info.major == 3:
        parse_url_func2 = parse_url3
    else:
        parse_url_func2 = parse_url2

    def handler(*args, **kwargs):
        addinfourl = None
        transaction = None
        url = None

        try:
            from urllib2 import Request
            from urllib import addinfourl
            transaction = agent.current_transaction()
            url = kwargs.get('url') or args[0]
            if isinstance(url, Request):
                url = url.get_full_url()
            if transaction is not None:
                o = parse_url_func2(url)
                transaction.profiler.external_call(
                    protocol=o.scheme,
                    host=o.hostname,
                    port=o.port or 80,
                    url=url,
                    caller='urllib2.urlopen',
                )
        except:
            pass

        ret = urlopen(*args, **kwargs)

        try:
            if transaction is not None:
                if isinstance(ret, addinfourl):
                    transaction.profiler.end(
                        message='urllib2.urlopen(url=%s,response=%s)' % (url, ret.code)
                    )
                else:
                    transaction.profiler.end()
        except:
            pass

        return ret
    return handler


def hook(urllib):
    if not sys.version_info.major == 2:
        return

    import urllib2
    urllib2.urlopen = wrap_urlopen(urllib2.urlopen)
