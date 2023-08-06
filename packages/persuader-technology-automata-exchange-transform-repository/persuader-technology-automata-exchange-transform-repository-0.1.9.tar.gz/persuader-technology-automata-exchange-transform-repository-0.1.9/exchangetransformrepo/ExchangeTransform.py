from dataclasses import dataclass


@dataclass
class ExchangeTransform:
    instrument: str
    transform: dict = None
    ignore: bool = False

    def __eq__(self, other):
        return self.instrument == other.instrument
