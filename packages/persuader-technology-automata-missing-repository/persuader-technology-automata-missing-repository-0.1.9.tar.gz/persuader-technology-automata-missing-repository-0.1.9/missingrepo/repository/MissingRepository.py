import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError

from missingrepo.Missing import Missing
from missingrepo.repository.serialize.missing_deserializer import deserialize_missing
from missingrepo.repository.serialize.missing_serializer import serialize_missing

MISSING_KEY = 'MISSING_KEY'


class MissingRepository:

    def __init__(self, options):
        self.log = logging.getLogger('MissingRepository')
        self.log.info('initializing')
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {MISSING_KEY}')
            raise MissingOptionError(f'missing option please provide options {MISSING_KEY}')
        if MISSING_KEY not in self.options:
            self.log.warning(f'missing option please provide option {MISSING_KEY}')
            raise MissingOptionError(f'missing option please provide option {MISSING_KEY}')

    def store_key(self):
        return self.options[MISSING_KEY]

    @staticmethod
    def value_key(missing):
        return f'{missing["missing"]}{missing["context"]}{missing["market"]}'.lower()

    def store(self, missings):
        serialized_entities = list([serialize_missing(missing) for missing in missings])
        print(f'serialized_entities -> {serialized_entities} value key:[{self.value_key(serialized_entities[0])}]')
        self.log.debug(f'Storing {len(serialized_entities)} missing')
        self.cache.values_store(self.store_key(), serialized_entities, custom_key=self.value_key)

    def create(self, missing):
        self.update(missing)

    def update(self, missing):
        serialized_entity = serialize_missing(missing)
        self.log.debug(f'setting value_key:[{self.value_key(serialized_entity)}] value:[{serialized_entity}] for store:[{self.store_key()}]')
        self.cache.values_set_value(self.store_key(), self.value_key(serialized_entity), serialized_entity)

    def delete(self, missing):
        serialized_entity = serialize_missing(missing)
        self.cache.values_delete_value(self.store_key(), self.value_key(serialized_entity))

    def retrieve(self) -> List[Missing]:
        serialized_entities = self.cache.values_fetch(self.store_key())
        deserialized_entities = list([deserialize_missing(se) for se in serialized_entities])
        self.log.debug(f'Retrieving {len(deserialized_entities)} missing')
        return deserialized_entities

    def is_already_missing(self, missing):
        serialized_entity = serialize_missing(missing)
        missing = self.cache.values_get_value(self.store_key(), self.value_key(serialized_entity))
        return missing is not None
