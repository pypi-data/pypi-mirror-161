from typing import Optional

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.number.BigFloat import BigFloat
from core.options.exception.MissingOptionError import MissingOptionError

INSTRUMENT_TRADE_FEE_KEY = 'INSTRUMENT_TRADE_FEE_KEY'


class InstrumentFeeRepository:

    def __init__(self, options):
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            raise MissingOptionError(f'missing option please provide options {INSTRUMENT_TRADE_FEE_KEY}')
        if INSTRUMENT_TRADE_FEE_KEY not in self.options:
            raise MissingOptionError(f'missing option please provide option {INSTRUMENT_TRADE_FEE_KEY}')

    def store_key(self):
        return self.options[INSTRUMENT_TRADE_FEE_KEY]

    @staticmethod
    def value_key(instrument_exchange):
        return f'{instrument_exchange}'

    def retrieve_instrument_trade_fee(self, instrument_exchange) -> Optional[BigFloat]:
        trade_fee = self.cache.values_get_value(self.store_key(), self.value_key(instrument_exchange))
        return BigFloat(trade_fee) if trade_fee is not None else None

    def store_instrument_trade_fee(self, fee, instrument_exchange):
        serialized_value = str(fee)
        self.cache.values_set_value(self.store_key(), self.value_key(instrument_exchange), serialized_value)

    def delete_instrument_trade_fee(self, instrument_exchange):
        self.cache.values_delete_value(self.store_key(), self.value_key(instrument_exchange))

    def retrieve_all(self):
        instrument_trade_fees = self.cache.values_fetch(self.store_key())
        if instrument_trade_fees is None:
            instrument_trade_fees = []
        return instrument_trade_fees

