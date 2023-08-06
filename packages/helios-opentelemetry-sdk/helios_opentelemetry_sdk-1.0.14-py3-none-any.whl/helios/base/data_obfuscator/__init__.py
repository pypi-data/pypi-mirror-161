from typing import Any

from helios.base.data_obfuscator.base_data_obfuscator import BaseDataObfuscator, DataObfuscatorConfiguration, Rules
from helios.base.data_obfuscator.redis_data_obfuscator import RedisDataObfuscator
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.util.types import Attributes


class DataObfuscator:
    def __init__(self, config: DataObfuscatorConfiguration) -> None:
        self.obfuscators_dict = self.create_obfuscators_dict(config)

    def obfuscate_data(self, span: ReadableSpan) -> None:
        attributes = span._attributes
        obfuscator = self._get_obfuscator(attributes)

        obfuscator.inject_data_obfuscation_flag(span)
        obfuscator.obfuscate_data(attributes)

    def _get_obfuscator(self, attributes: Attributes) -> BaseDataObfuscator:
        db_system = attributes.get('db.system', None)
        return self.obfuscators_dict.get(db_system, self.obfuscators_dict['default'])

    @staticmethod
    def hash(key: str, msg: Any, length: int = 8) -> str:
        return BaseDataObfuscator.hash(key, msg, length)

    @staticmethod
    def create_obfuscators_dict(config: DataObfuscatorConfiguration) -> dict:
        obfuscators_dict = {
            'redis': RedisDataObfuscator(config),
            'default': BaseDataObfuscator(config),
        }

        return obfuscators_dict


__all__ = ['DataObfuscator', 'DataObfuscatorConfiguration', 'Rules']
