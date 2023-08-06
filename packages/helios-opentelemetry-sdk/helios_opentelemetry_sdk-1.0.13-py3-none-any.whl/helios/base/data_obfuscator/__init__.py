from typing import Any

from helios.base.data_obfuscator.base_data_obfuscator import BaseDataObfuscator, DataObfuscatorConfiguration, Rules
from helios.base.data_obfuscator.redis_data_obfuscator import RedisDataObfuscator
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.util.types import AttributeValue


class DataObfuscator:
    def __init__(self, config: DataObfuscatorConfiguration) -> None:
        self.obfuscators_dict = self.create_obfuscators_dict(config)

    def obfuscate_data(self, span: ReadableSpan) -> None:
        attributes = span._attributes
        otel_library_name = attributes.get('otel.library.name', None)
        obfuscator = self._get_obfuscator(otel_library_name)

        obfuscator.inject_data_obfuscation_flag(span)
        obfuscator.obfuscate_data(attributes)

    def _get_obfuscator(self, otel_library_name: AttributeValue) -> BaseDataObfuscator:
        return self.obfuscators_dict.get(otel_library_name, self.obfuscators_dict['default'])

    @staticmethod
    def hash(key: str, msg: Any, length: int = 8) -> str:
        return BaseDataObfuscator.hash(key, msg, length)

    @staticmethod
    def create_obfuscators_dict(config: DataObfuscatorConfiguration) -> dict:
        obfuscators_dict = {
            '@opentelemetry/instrumentation-redis': RedisDataObfuscator(config),
            'default': BaseDataObfuscator(config),
        }

        return obfuscators_dict


__all__ = ['DataObfuscator', 'DataObfuscatorConfiguration', 'Rules']
