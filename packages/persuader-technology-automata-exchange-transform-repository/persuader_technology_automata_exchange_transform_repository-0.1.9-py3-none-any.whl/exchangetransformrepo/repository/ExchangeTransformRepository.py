import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError

from exchangetransformrepo.ExchangeTransform import ExchangeTransform
from exchangetransformrepo.repository.serialize.exchange_transform_deserializer import deserialize_exchange_transform
from exchangetransformrepo.repository.serialize.exchange_transform_serializer import serialize_exchange_transform

EXCHANGE_TRANSFORMATIONS_KEY = 'EXCHANGE_TRANSFORMATIONS_KEY'


class ExchangeTransformRepository:

    def __init__(self, options):
        self.log = logging.getLogger('ExchangeTransformRepository')
        self.log.info('initializing')
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {EXCHANGE_TRANSFORMATIONS_KEY}')
            raise MissingOptionError(f'missing option please provide options {EXCHANGE_TRANSFORMATIONS_KEY}')
        if EXCHANGE_TRANSFORMATIONS_KEY not in self.options:
            self.log.warning(f'missing option please provide option {EXCHANGE_TRANSFORMATIONS_KEY}')
            raise MissingOptionError(f'missing option please provide option {EXCHANGE_TRANSFORMATIONS_KEY}')

    def store_key(self):
        return self.options[EXCHANGE_TRANSFORMATIONS_KEY]

    @staticmethod
    def value_key(exchange_transform):
        return f'{exchange_transform["instrument"]}'

    def create(self, exchange_transform):
        self.update(exchange_transform)

    def update(self, exchange_transform):
        self.log.debug(f'setting exchange transform [{exchange_transform}]')
        serialized_entity = serialize_exchange_transform(exchange_transform)
        self.cache.values_set_value(self.store_key(), self.value_key(serialized_entity), serialized_entity)

    def delete(self, exchange_transform):
        serialized_entity = serialize_exchange_transform(exchange_transform)
        self.cache.values_delete_value(self.store_key(), self.value_key(serialized_entity))

    def store_all(self, exchange_transforms):
        self.log.debug(f'overwriting exchange transforms [{len(exchange_transforms)}]')
        serialized_entities = list([serialize_exchange_transform(exchange_transform) for exchange_transform in exchange_transforms])
        self.cache.values_store(self.store_key(), serialized_entities, custom_key=self.value_key)

    def retrieve(self) -> List[ExchangeTransform]:
        raw_entities = self.cache.values_fetch(self.store_key())
        entities = list([deserialize_exchange_transform(raw) for raw in raw_entities])
        self.log.debug(f'Retrieving exchange transforms [{len(entities)}]')
        return entities
