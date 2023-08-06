from json import JSONDecoder, dumps
from typing import List
from opentelemetry.util.types import AttributeValue, Attributes

from helios.base.data_obfuscator.base_data_obfuscator import BaseDataObfuscator
from helios.base.span_attributes import SpanAttributes


class RedisDataObfuscator(BaseDataObfuscator):
    def obfuscate_data(self, attributes: Attributes) -> None:
        if SpanAttributes.DB_STATEMENT in attributes:
            db_statement = attributes[SpanAttributes.DB_STATEMENT]

            attributes[SpanAttributes.DB_STATEMENT] = self._obfuscate_redis_statement(db_statement)

        if SpanAttributes.DB_QUERY_RESULT in attributes:
            # TODO: support MGET (returns array of values)
            attributes[SpanAttributes.DB_QUERY_RESULT] = self._obfuscate_datum(attributes[SpanAttributes.DB_QUERY_RESULT])

    def _obfuscate_redis_statement(self, db_statement: AttributeValue) -> AttributeValue:
        if not isinstance(db_statement, str):
            return self._obfuscate_datum(db_statement)

        obfuscated_json_strings = []
        try:
            for json_object in extract_json_objects(db_statement):
                json_string = dumps(json_object)
                obfuscated_json_string = self._obfuscate_datum(json_string)
                obfuscated_json_strings.append(obfuscated_json_string)
            db_statement = replace_json_strings(db_statement, obfuscated_json_strings)
        except Exception as exception:
            print(exception)
            db_statement = self._obfuscate_datum(db_statement)

        return db_statement


def extract_json_objects(text: str, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.
    """
    scanner_pos = 0
    while True:
        json_start_idx = text.find('{', scanner_pos)
        if json_start_idx == -1:
            break
        try:
            # raw_decode decodes a json string that might have extra characters after the end of the json
            json_result, json_length = decoder.raw_decode(text[json_start_idx:])
            yield json_result
            scanner_pos = json_start_idx + json_length
        except ValueError:
            scanner_pos = json_start_idx + 1


def replace_json_strings(text: str, new_json_strings: List[str], decoder=JSONDecoder()):
    """Finds again the json strings in the text, and replaces with the new json strings, in order"""
    scanner_pos = 0
    while True:
        json_start_idx = text.find('{', scanner_pos)
        if json_start_idx == -1:
            break
        try:
            # raw_decode decodes a json string that might have extra characters after the end of the json
            _, json_length = decoder.raw_decode(text[json_start_idx:])
            new_json_string = new_json_strings.pop(0)
            text = text[0:json_start_idx] + new_json_string + text[json_start_idx + json_length:]
            scanner_pos = json_start_idx + len(new_json_string)
        except ValueError:
            scanner_pos = json_start_idx + 1
    return text
