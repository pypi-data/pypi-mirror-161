import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError

from processrepo.Process import Process
from processrepo.repository.serialize.process_deserializer import deserialize_process
from processrepo.repository.serialize.process_serializer import serialize_process

PROCESS_KEY = 'PROCESS_KEY'


class ProcessRepository:

    def __init__(self, options):
        self.log = logging.getLogger('ProcessRepository')
        self.options = options
        self.__check_options()
        self.process_key = self.options[PROCESS_KEY]
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {PROCESS_KEY}')
            raise MissingOptionError(f'missing option please provide options {PROCESS_KEY}')
        if PROCESS_KEY not in self.options:
            self.log.warning(f'missing option please provide option {PROCESS_KEY}')
            raise MissingOptionError(f'missing option please provide option {PROCESS_KEY}')

    def store_key(self):
        return self.options[PROCESS_KEY]

    @staticmethod
    def value_key(process):
        return f'{process["market"]}-{process["name"]}'

    def store(self, process: Process):
        serialized_entity = serialize_process(process)
        self.cache.values_set_value(self.store_key(), self.value_key(serialized_entity), serialized_entity)

    def retrieve(self, process_name, market) -> Process:
        serialized_for_get = {"market": market, "name": process_name}
        serialized_entity = self.cache.values_get_value(self.store_key(), self.value_key(serialized_for_get))
        return deserialize_process(serialized_entity)

    def retrieve_all(self) -> List[Process]:
        all_serialized = self.cache.values_fetch(self.store_key())
        return list([deserialize_process(sp) for sp in all_serialized])
