import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError

from tradetransformrepo.TradeTransform import TradeTransform
from tradetransformrepo.repository.serialize.trade_transform_deserializer import deserialize_trade_transform
from tradetransformrepo.repository.serialize.trade_transform_serializer import serialize_trade_transform

TRADE_TRANSFORMATIONS_KEY = 'TRADE_TRANSFORMATIONS_KEY'


class TradeTransformRepository:

    def __init__(self, options):
        self.log = logging.getLogger('TradeTransformRepository')
        self.log.info('initializing')
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {TRADE_TRANSFORMATIONS_KEY}')
            raise MissingOptionError(f'missing option please provide options {TRADE_TRANSFORMATIONS_KEY}')
        if TRADE_TRANSFORMATIONS_KEY not in self.options:
            self.log.warning(f'missing option please provide option {TRADE_TRANSFORMATIONS_KEY}')
            raise MissingOptionError(f'missing option please provide option {TRADE_TRANSFORMATIONS_KEY}')

    def store_key(self):
        return self.options[TRADE_TRANSFORMATIONS_KEY]

    @staticmethod
    def value_key(transform):
        return f'{transform["trade"]}'

    def create(self, transform):
        self.update(transform)

    def update(self, transform):
        self.log.debug(f'setting trade transform:[{transform}]')
        serialized_entity = serialize_trade_transform(transform)
        self.cache.values_set_value(self.store_key(), self.value_key(serialized_entity), serialized_entity)

    def delete(self, transform):
        serialized_entity = serialize_trade_transform(transform)
        self.cache.values_delete_value(self.store_key(), self.value_key(serialized_entity))

    def store_all(self, transformations):
        self.log.debug(f'storing trade transform:[{len(transformations)}]')
        serialized_entities = list([serialize_trade_transform(tt) for tt in transformations])
        self.cache.values_store(self.store_key(), serialized_entities, custom_key=self.value_key)

    def retrieve(self) -> List[TradeTransform]:
        serialized_entities = self.cache.values_fetch(self.store_key())
        entities = list([deserialize_trade_transform(se) for se in serialized_entities])
        self.log.debug(f'retrieving trade transforms:[{len(entities)}]')
        return entities
