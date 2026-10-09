from dataclasses import asdict, dataclass
from threading import RLock
import time

from config import TARGET_MAX, TARGET_MIN
from emg.processor import EMGProcessor


@dataclass
class GameState:
    biceps: float = 0.0
    triceps: float = 0.0
    overall_activation: float = 0.0
    balance: float = 0.0
    fatigue: float = 0.0
    score: int = 0
    game_time: float = 0.0
    game_state: str = "READY"
    input_mode: str = "keyboard"
    target_min: float = TARGET_MIN
    target_max: float = TARGET_MAX


class GameController:
    VALID_MODES = {"keyboard", "slider", "auto"}

    def __init__(self):
        self.state = GameState()
        self.processor = EMGProcessor()
        self._lock = RLock()
        self._started_at: float | None = None
        self._elapsed = 0.0

    def update_emg(self, biceps: float, triceps: float, input_mode: str | None = None) -> dict:
        with self._lock:
            result = self.processor.process(biceps, triceps)
            for key, value in asdict(result).items():
                setattr(self.state, key, value)
            if input_mode in self.VALID_MODES:
                self.state.input_mode = input_mode
            return self.snapshot()

    def set_game_state(self, action: str) -> dict:
        with self._lock:
            now = time.monotonic()
            if action == "start" and self.state.game_state in {"READY", "PAUSED"}:
                self._started_at = now
                self.state.game_state = "PLAYING"
            elif action == "pause" and self.state.game_state == "PLAYING":
                self._elapsed += now - (self._started_at or now)
                self._started_at = None
                self.state.game_state = "PAUSED"
            return self.snapshot()

    def add_score(self, points: int = 100) -> dict:
        with self._lock:
            if self.state.game_state == "PLAYING":
                self.state.score += max(0, int(points))
            return self.snapshot()

    def reset(self) -> dict:
        with self._lock:
            mode = self.state.input_mode
            self.processor.reset()
            self.state = GameState(input_mode=mode)
            self._started_at = None
            self._elapsed = 0.0
            return self.snapshot()

    def snapshot(self) -> dict:
        data = asdict(self.state)
        elapsed = self._elapsed
        if self.state.game_state == "PLAYING" and self._started_at is not None:
            elapsed += time.monotonic() - self._started_at
        data["game_time"] = round(elapsed, 1)
        return data

