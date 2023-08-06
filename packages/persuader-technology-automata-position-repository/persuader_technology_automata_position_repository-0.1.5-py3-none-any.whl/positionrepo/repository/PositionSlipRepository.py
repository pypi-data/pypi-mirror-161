import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.options.exception.MissingOptionError import MissingOptionError
from core.position.PositionSlip import PositionSlip

from positionrepo.repository.serialize.position_slip_deserializer import deserialize
from positionrepo.repository.serialize.position_slip_serializer import serialize

POSITION_SLIP_KEY = 'POSITION_SLIP_KEY'


class PositionSlipRepository:

    def __init__(self, options):
        self.log = logging.getLogger('PositionSlipRepository')
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            raise MissingOptionError(f'missing option please provide options {POSITION_SLIP_KEY}')
        if POSITION_SLIP_KEY not in self.options:
            raise MissingOptionError(f'missing option please provide option {POSITION_SLIP_KEY}')

    def store_key(self):
        return self.options[POSITION_SLIP_KEY]

    def store(self, position_slip: PositionSlip):
        slip_serialized = serialize(position_slip)
        self.log.debug(f'storing position slip:{slip_serialized}')
        self.cache.store(self.store_key(), slip_serialized)

    def retrieve(self) -> PositionSlip:
        serialized_slip = self.cache.fetch(self.store_key(), as_type=dict)
        self.log.debug(f'retrieving position slip:{serialized_slip}')
        return deserialize(serialized_slip)
