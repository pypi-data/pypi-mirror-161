import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError
from core.position.Position import Position
from coreutility.string.string_utility import is_empty

from positionrepo.repository.serialize.position_deserializer import deserialize
from positionrepo.repository.serialize.position_serializer import serialize

POSITION_KEY = 'POSITION_KEY'
POSITION_HISTORY_LIMIT = 'POSITION_HISTORY_LIMIT'


class PositionRepository:

    def __init__(self, options):
        self.log = logging.getLogger('PositionRepository')
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            raise MissingOptionError(f'missing option please provide options {POSITION_KEY}')
        if POSITION_KEY not in self.options:
            raise MissingOptionError(f'missing option please provide option {POSITION_KEY}')

    def store_key(self):
        return self.options[POSITION_KEY]

    def store_history_key(self):
        position_key = self.store_key()
        return f'{position_key}:mv:history'

    @staticmethod
    def historic_value_key(position):
        return f'{position["instant"]}'

    def store(self, position: Position):
        position_serialized = serialize(position)
        self.cache.store(self.store_key(), position_serialized)
        self.store_historical_position(position)

    def retrieve(self) -> Position:
        raw_position = self.cache.fetch(self.store_key(), as_type=dict)
        return deserialize(raw_position)

    def store_historical_position(self, position: Position):
        if is_empty(position.exchanged_from) is False:
            serialized_entity = serialize(position)
            self.log.debug(f'storing position into history:{serialized_entity} in store[{self.store_history_key()}] for key:{self.historic_value_key(serialized_entity)}')
            self.cache.values_set_value(self.store_history_key(), self.historic_value_key(serialized_entity), serialized_entity)
            self.__expunge_old_historical_positions()

    def retrieve_historic_positions(self):
        raw_entities = self.cache.values_fetch(self.store_history_key())
        return list([deserialize(raw) for raw in raw_entities])

    def __expunge_old_historical_positions(self):
        historical_positions = self.cache.values_fetch(self.store_history_key())
        limit = int(self.options[POSITION_HISTORY_LIMIT])
        if len(historical_positions) > limit:
            historical_positions.sort(reverse=True, key=self.historic_value_key)
            history_positions_to_delete = historical_positions[limit:]
            for hp in history_positions_to_delete:
                self.cache.values_delete_value(self.store_history_key(), self.historic_value_key(hp))
