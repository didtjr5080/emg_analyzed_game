from abc import ABC, abstractmethod


class EMGProvider(ABC):
    """Replaceable source of normalized two-channel EMG activation."""

    @abstractmethod
    def get_sample(self) -> tuple[float, float]:
        raise NotImplementedError

