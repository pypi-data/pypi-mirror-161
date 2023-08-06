import logging

from cache.holder.RedisCacheHolder import RedisCacheHolder
from cache.provider.RedisCacheProviderWithHash import RedisCacheProviderWithHash
from core.options.exception.MissingOptionError import MissingOptionError
from core.trade.InstrumentTrade import InstrumentTrade, Status
from coreutility.string.string_utility import is_empty

from traderepo.repository.serialize.trade_deserializer import deserialize_trade
from traderepo.repository.serialize.trade_serializer import serialize_trade

TRADE_KEY = 'TRADE_KEY'
TRADE_HISTORY_LIMIT = 'TRADE_HISTORY_LIMIT'


class TradeRepository:

    def __init__(self, options):
        self.log = logging.getLogger('TradeRepository')
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder(held_type=RedisCacheProviderWithHash)

    def __check_options(self):
        if self.options is None:
            raise MissingOptionError(f'missing option please provide options {TRADE_KEY}')
        if TRADE_KEY not in self.options:
            raise MissingOptionError(f'missing option please provide option {TRADE_KEY}')

    def store_key(self):
        return self.options[TRADE_KEY]

    def store_history_key(self):
        store_key = self.store_key()
        return f'{store_key}:mv:history'

    @staticmethod
    def historic_value_key(trade):
        return f'{trade["instant"]}'

    def store_trade(self, trade: InstrumentTrade):
        trade_to_store = serialize_trade(trade)
        self.cache.store(self.store_key(), trade_to_store)
        self.store_historical_trade(trade)

    def retrieve_trade(self) -> InstrumentTrade:
        serialized_trade = self.cache.fetch(self.store_key(), as_type=dict)
        return deserialize_trade(serialized_trade)

    def retrieve_historic_trades(self):
        serialized_entities = self.cache.values_fetch(self.store_history_key())
        return list([deserialize_trade(se) for se in serialized_entities])

    def store_historical_trade(self, trade: InstrumentTrade):
        if trade.status == Status.EXECUTED and is_empty(trade.order_id) is False:
            serialized_entity = serialize_trade(trade)
            self.log.debug(f'storing trade into history:{serialized_entity} in store[{self.store_history_key()}] for key:{self.historic_value_key(serialized_entity)}')
            self.cache.values_set_value(self.store_history_key(), self.historic_value_key(serialized_entity), serialized_entity)
            self.__expunge_old_historical_trades()

    def __expunge_old_historical_trades(self):
        if TRADE_HISTORY_LIMIT in self.options:
            historical_trades = self.cache.values_fetch(self.store_history_key())
            limit = int(self.options[TRADE_HISTORY_LIMIT])
            if len(historical_trades) > limit:
                historical_trades.sort(reverse=True, key=self.historic_value_key)
                history_trades_to_delete = historical_trades[limit:]
                for ht in history_trades_to_delete:
                    self.cache.values_delete_value(self.store_history_key(), self.historic_value_key(ht))
