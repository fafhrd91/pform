from unittest import TestCase
from pyramid import testing
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRequestExtensions

def strip(text):
    return ' '.join([s.strip() for s in text.split('\n')])


class BaseTestCase(TestCase):

    _settings = {}
    _environ = {
        'wsgi.url_scheme':'http',
        'wsgi.version':(1,0),
        'HTTP_HOST': 'example.com',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/'}
    registry = None

    def setUp(self):
        self.init_pyramid()

    def make_request(self, registry=None,
                     environ=None, request_iface=IRequest, **kwargs):
        if registry is None:
            registry = self.registry
        if environ is None:
            environ=self._environ
        request = testing.DummyRequest(environ=dict(environ), **kwargs)
        request.request_iface = IRequest
        request.registry = registry
        request._set_extensions(registry.getUtility(IRequestExtensions))
        return request

    def init_extensions(self, registry):
        from pyramid.config.factories import _RequestExtensions

        exts = registry.queryUtility(IRequestExtensions)
        if exts is None:
            exts = _RequestExtensions()
            self.registry.registerUtility(exts, IRequestExtensions)

    def init_pyramid(self):
        self.config = testing.setUp(settings=self._settings, autocommit=True)
        self.config.get_routes_mapper()
        self.config.include('player')
        self.config.include('pform')
        self.init_extensions(self.config.registry)

        self.registry = self.config.registry
        self.request = self.make_request()
        self.config.begin(request=self.request)
