import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.exchange.InstrumentExchange import InstrumentExchange
from core.options.exception.MissingOptionError import MissingOptionError
from exchange.InstrumentExchangesHolder import InstrumentExchangesHolder

INSTRUMENT_EXCHANGES_KEY = 'INSTRUMENT_EXCHANGES_KEY'


class InstrumentExchangeRepository:

    def __init__(self, options):
        self.log = logging.getLogger('InstrumentExchangeRepository')
        self.options = options
        self.__check_options()
        self.instrument_exchanges_key = options[INSTRUMENT_EXCHANGES_KEY]
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'Instrument Exchange Repository missing option please provide options {INSTRUMENT_EXCHANGES_KEY}')
            raise MissingOptionError(f'Instrument Exchange Repository missing option please provide options {INSTRUMENT_EXCHANGES_KEY}')
        if INSTRUMENT_EXCHANGES_KEY not in self.options:
            self.log.warning(f'Instrument Exchange Repository missing option please provide option {INSTRUMENT_EXCHANGES_KEY}')
            raise MissingOptionError(f'Instrument Exchange Repository missing option please provide option {INSTRUMENT_EXCHANGES_KEY}')

    def store_key(self):
        return self.options[INSTRUMENT_EXCHANGES_KEY]

    @staticmethod
    def value_key(instrument_exchange):
        return f'{instrument_exchange[0]}{instrument_exchange[1]}'

    def store(self, instrument_exchanges: InstrumentExchangesHolder):
        all_exchanges = instrument_exchanges.get_all()
        serialized = list([[ie.instrument, ie.to_instrument] for ie in all_exchanges])
        self.cache.values_store(self.store_key(), serialized, custom_key=self.value_key)

    def create(self, instrument_exchange: InstrumentExchange):
        self.update(instrument_exchange)

    def update(self, instrument_exchange: InstrumentExchange):
        serialized_entity = [instrument_exchange.instrument, instrument_exchange.to_instrument]
        self.cache.values_set_value(self.store_key(), self.value_key(serialized_entity), serialized_entity)

    def delete(self, instrument_exchange: InstrumentExchange):
        serialized_entity = [instrument_exchange.instrument, instrument_exchange.to_instrument]
        self.cache.values_delete_value(self.store_key(), self.value_key(serialized_entity))

    def retrieve(self) -> InstrumentExchangesHolder:
        serialized = self.cache.values_fetch(self.store_key())
        holder = InstrumentExchangesHolder()
        for serialized_instrument_exchange in serialized:
            (instrument, to_instrument) = tuple(serialized_instrument_exchange)
            holder.add(InstrumentExchange(instrument, to_instrument))
        return holder
