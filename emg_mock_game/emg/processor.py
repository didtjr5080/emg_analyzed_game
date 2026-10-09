from dataclasses import dataclass

from config import FATIGUE_INCREASE, FATIGUE_RECOVERY, FATIGUE_THRESHOLD


@dataclass(frozen=True)
class EMGResult:
    biceps: float
    triceps: float
    overall_activation: float
    balance: float
    fatigue: float


class EMGProcessor:
    """Normalizes activation and maintains a game-only fatigue estimate."""

    def __init__(self, fatigue: float = 0.0):
        self.fatigue = self.clamp(fatigue)

    @staticmethod
    def clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def process(self, biceps: float, triceps: float) -> EMGResult:
        biceps = self.clamp(biceps)
        triceps = self.clamp(triceps)
        overall = (biceps + triceps) / 2.0
        delta = FATIGUE_INCREASE if overall > FATIGUE_THRESHOLD else -FATIGUE_RECOVERY
        self.fatigue = self.clamp(self.fatigue + delta)
        return EMGResult(biceps, triceps, overall, biceps - triceps, self.fatigue)

    def reset(self) -> None:
        self.fatigue = 0.0

