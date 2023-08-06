from dataclasses import dataclass

from core.exchange.InstrumentExchange import InstrumentExchange
from core.number.BigFloat import BigFloat


@dataclass
class ExchangeRate(InstrumentExchange):
    rate: BigFloat = None

    def inverse(self):
        return BigFloat('1.0') / self.rate

    def __iter__(self):
        return iter((self.instrument, self.to_instrument, self.rate))
