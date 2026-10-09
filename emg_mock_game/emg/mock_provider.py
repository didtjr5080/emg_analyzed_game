import math
import random
import time

from .provider import EMGProvider


class MockEMGProvider(EMGProvider):
    """Generates alternating, noisy contraction cycles for UI demonstrations."""

    def __init__(self, seed: int | None = None):
        self._random = random.Random(seed)
        self._started = time.monotonic()

    def get_sample(self) -> tuple[float, float]:
        elapsed = time.monotonic() - self._started
        phase = elapsed * 0.85
        envelope = max(0.0, math.sin(phase)) ** 1.5
        alternate = max(0.0, math.sin(phase + math.pi)) ** 1.5
        biceps = 0.08 + 0.68 * envelope + self._random.uniform(-0.035, 0.035)
        triceps = 0.08 + 0.68 * alternate + self._random.uniform(-0.035, 0.035)
        return self._clamp(biceps), self._clamp(triceps)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

