import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError

from processrepo.ProcessRunProfile import ProcessRunProfile
from processrepo.repository.serialize.process_run_profile_deserializer import deserialize_process_run_profile
from processrepo.repository.serialize.process_run_profile_serializer import serialize_process_run_profile

PROCESS_RUN_PROFILE_KEY = 'PROCESS_RUN_PROFILE_KEY'


class ProcessRunProfileRepository:

    def __init__(self, options):
        self.log = logging.getLogger('ProcessRunProfileRepository')
        self.options = options
        self.__check_options()
        self.process_run_profile_key = self.options[PROCESS_RUN_PROFILE_KEY]
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {PROCESS_RUN_PROFILE_KEY}')
            raise MissingOptionError(f'missing option please provide options {PROCESS_RUN_PROFILE_KEY}')
        if PROCESS_RUN_PROFILE_KEY not in self.options:
            self.log.warning(f'missing option please provide option {PROCESS_RUN_PROFILE_KEY}')
            raise MissingOptionError(f'missing option please provide option {PROCESS_RUN_PROFILE_KEY}')

    def store_key(self):
        return self.options[PROCESS_RUN_PROFILE_KEY]

    @staticmethod
    def value_key(process_run_profile):
        return f'{process_run_profile["market"]}-{process_run_profile["name"]}'

    def store(self, process_run_profile: ProcessRunProfile):
        serialized_entity = serialize_process_run_profile(process_run_profile)
        self.cache.values_set_value(self.store_key(), self.value_key(serialized_entity), serialized_entity)

    def retrieve(self, process_name, market) -> ProcessRunProfile:
        serialized_for_get = {"market": market, "name": process_name}
        serialized_entity = self.cache.values_get_value(self.store_key(), self.value_key(serialized_for_get))
        return deserialize_process_run_profile(serialized_entity, market, process_name)
