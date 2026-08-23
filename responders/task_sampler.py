from __future__ import annotations

import random as _random
from dataclasses import dataclass, field
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    continue_key: str = "space"
    accuracy: float = 0.88
    rt_mean_s: float = 0.72
    rt_sd_s: float = 0.12
    forced_error_trials: list[int] = field(default_factory=list)
    forced_timeout_trials: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _draw(self) -> float:
        return float(self._rng.random()) if hasattr(self._rng, "random") else _random.random()

    def _rt(self) -> float:
        if hasattr(self._rng, "normal"):
            return max(0.005, float(self._rng.normal(self.rt_mean_s, self.rt_sd_s)))
        if hasattr(self._rng, "gauss"):
            return max(0.005, float(self._rng.gauss(self.rt_mean_s, self.rt_sd_s)))
        return self.rt_mean_s

    def act(self, obs: Observation) -> Action:
        keys = [str(key) for key in list(obs.valid_keys or [])]
        if not keys:
            return Action(key=None, rt_s=None, meta={"source": "word_superiority_sampler", "reason": "no_valid_keys"})
        factors = dict(getattr(obs, "task_factors", {}) or {})
        stage = str(factors.get("stage", getattr(obs, "phase", "")))
        if stage in {"instruction", "block_break", "good_bye"}:
            key = self.continue_key if self.continue_key in keys else keys[0]
            return Action(key=key, rt_s=0.05)
        if stage != "letter_probe":
            return Action(key=None, rt_s=None)

        raw_trial_id = getattr(obs, "trial_id", -1)
        trial_id = int(raw_trial_id) if str(raw_trial_id).lstrip("-").isdigit() else -1
        if trial_id in set(self.forced_timeout_trials):
            return Action(key=None, rt_s=None, meta={"source": "word_superiority_sampler", "outcome": "forced_timeout"})
        correct_key = str(factors.get("correct_key", keys[0]))
        make_error = trial_id in set(self.forced_error_trials) or self._draw() > self.accuracy
        response_key = next((key for key in keys if key != correct_key), correct_key) if make_error else correct_key
        return Action(key=response_key, rt_s=self._rt(), meta={"source": "word_superiority_sampler", "correct": not make_error})
