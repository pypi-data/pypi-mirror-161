import re
from sys import modules
from logging import getLogger

from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.util.http import parse_excluded_urls

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor

_LOG = getLogger(__name__)


class HeliosTornadoInstrumentor(HeliosBaseHttpInstrumentor):
    CLASS_NAME = 'TornadoInstrumentor'
    MODULE_NAME = 'opentelemetry.instrumentation.tornado'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.CLASS_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        # tornado instrumentation holds excluded_urls as a module var rather than taking in an arg to instrument()
        if modules[HeliosTornadoInstrumentor.MODULE_NAME] is not None:
            setattr(modules[HeliosTornadoInstrumentor.MODULE_NAME], '_excluded_urls', parse_excluded_urls(kwargs.get('excluded_urls')))

        self.get_instrumentor().instrument(
            server_request_hook=self.server_request_hook,
            client_request_hook=self.client_request_hook,
            client_response_hook=self.client_response_hook,
            tracer_provider=tracer_provider)

    def client_request_hook(self, span, request):
        try:
            HeliosBaseHttpInstrumentor.base_request_hook(span, dict(request.headers), request.body)
        except Exception as error:
            _LOG.debug('tornado client_request_hook instrumentation error: %s.', error)

    def client_response_hook(self, span, response):
        try:
            if getattr(response, '_state', None) != 'FINISHED':
                return

            result = response.result()
            if type(result.body) == bytes:
                body = str(result.body)
            elif type(result.body) == str:
                body = result.body
            else:
                body = None
            HeliosBaseHttpInstrumentor.base_response_hook(span, dict(result.headers), body)
        except Exception as error:
            _LOG.debug('tornado client_response_hook instrumentation error: %s.', error)

    def server_request_hook(self, span, handler):
        try:
            if handler.request is None:
                return

            route = self.extract_http_route(handler)
            span.set_attribute(SpanAttributes.HTTP_ROUTE, route) if route else None
            span.set_attribute(SpanAttributes.HTTP_URL, handler.request.full_url())
            request_payload = None if handler.request.body is None else handler.request.body.decode('utf-8')
            HeliosBaseHttpInstrumentor.base_request_hook(span, handler.request.headers, request_payload)
        except Exception as error:
            _LOG.debug('tornado server_request instrumentation error: %s.', error)

    @staticmethod
    def extract_http_route(handler):
        if (
            handler.application is None or
            handler.application.wildcard_router is None or
            handler.application.wildcard_router.rules is None or
            handler.request is None or
            handler.request.path is None
        ):
            return None

        for rule in handler.application.wildcard_router.rules:
            # noinspection PyBroadException
            try:
                # noinspection PyProtectedMember
                _path = rule.matcher._path

                if re.compile(_path).match(handler.request.path):
                    return _path
            except Exception:
                pass
