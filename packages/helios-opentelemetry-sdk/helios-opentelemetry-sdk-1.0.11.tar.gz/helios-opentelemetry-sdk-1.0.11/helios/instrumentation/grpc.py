from logging import getLogger
from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor

_LOG = getLogger(__name__)


class HeliosGrpcClientInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.grpc'
    INSTRUMENTOR_NAME = 'GrpcInstrumentorClient'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)


class HeliosGrpcServerInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.grpc'
    INSTRUMENTOR_NAME = 'GrpcInstrumentorServer'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)
