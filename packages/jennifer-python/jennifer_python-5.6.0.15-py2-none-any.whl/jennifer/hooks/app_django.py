from jennifer.wrap.wsgi import wrap_wsgi_app
from jennifer.agent import jennifer_agent
from jennifer.api.format import format_function
from distutils.version import LooseVersion

__hooking_module__ = 'django'
__minimum_python_version__ = LooseVersion("2.7")


def hook(django_module):
    from django.core.handlers.wsgi import WSGIHandler

    def wrap_wsgi_handler_class(origin_wsgi_entry_func):
        def handler(self, environ, start_response):
            resolver = None
            origin_path_info = environ.get('PATH_INFO')
            request = self.request_class(environ)
            if hasattr(django_module, 'urls') and hasattr(django_module.urls, 'get_resolver'):
                get_resolver = django_module.urls.get_resolver
                if hasattr(request, 'urlconf'):
                    urlconf = request.urlconf
                    resolver = get_resolver(urlconf)
                else:
                    resolver = get_resolver()
            elif hasattr(django_module.core, 'urlresolvers'):
                url_resolvers = django_module.core.urlresolvers
                settings = django_module.conf.settings
                urlconf = settings.ROOT_URLCONF
                url_resolvers.set_urlconf(urlconf)
                resolver = url_resolvers.RegexURLResolver(r'^/', urlconf)
                if hasattr(request, 'urlconf'):
                    urlconf = request.urlconf
                    url_resolvers.set_urlconf(urlconf)
                    resolver = url_resolvers.RegexURLResolver(r'^/', urlconf)

            profiler = None

            if resolver is not None:
                try:
                    agent = jennifer_agent()
                    if agent is not None:
                        profiler = agent.current_transaction().profiler

                    try:
                        resolver_match = resolver.resolve(request.path_info)
                        name = format_function(resolver_match.func)

                        if profiler is not None:
                            profiler.set_root_name(name)
                    except:
                        pass

                except:
                    if profiler is not None:
                        profiler.set_root_name(request.path_info)
                    pass

                # origin_path_info: '/static/bbs/custom.css'
                # request.path: u'/static/bbs/custom.css'
                # request.get_full_path(): u'/static/bbs/custom.css'
                # request.build_absolute_uri(): 'http://localhost:18091/static/bbs/custom.css'

                if profiler is not None:
                    user_request_url = request.build_absolute_uri()
                    profiler.message('request url == %s' % (user_request_url,))

            if origin_path_info is not None:
                environ['PATH_INFO'] = origin_path_info

            return origin_wsgi_entry_func(self, environ, start_response)

        return handler

    WSGIHandler.__call__ = wrap_wsgi_handler_class(WSGIHandler.__call__)
    WSGIHandler.__call__ = wrap_wsgi_app(WSGIHandler.__call__)  # , 'django.core.handlers.wsgi.WSGIHandler.__call__')
