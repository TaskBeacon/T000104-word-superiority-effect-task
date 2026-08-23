from __future__ import annotations

import random
from typing import Any

from psychopy import visual
from psychopy.visual.basevisual import BaseVisualStim


class LetterArrayStim(BaseVisualStim):
    """Four fixed spatial slots so words and isolated letters share geometry."""

    def __init__(self, win, *, display_text: str, slot_x: list[float], letter_height: float, font: str) -> None:
        super().__init__(win, units="deg", name="letter_array", autoLog=False)
        slots = display_text.split("|") if "|" in display_text else list(display_text)
        if len(slots) != 4:
            raise ValueError("LetterArrayStim requires exactly four slots")
        self.letters = [
            visual.TextStim(
                win,
                text=str(letter),
                pos=(float(x), 0.0),
                height=float(letter_height),
                font=str(font),
                color="black",
                units="deg",
                autoLog=False,
            )
            for x, letter in zip(slot_x, slots)
            if letter
        ]

    def draw(self) -> None:
        for letter in self.letters:
            letter.draw()


class PatternMaskStim(BaseVisualStim):
    """Deterministic high-contrast field of irregular line fragments."""

    def __init__(
        self,
        win,
        *,
        seed: int,
        width_deg: float,
        height_deg: float,
        fragment_count: int,
        line_width: float,
    ) -> None:
        super().__init__(win, units="deg", name="pattern_mask", autoLog=False)
        rng = random.Random(int(seed))
        self.border = visual.Rect(
            win,
            width=float(width_deg),
            height=float(height_deg),
            fillColor="white",
            lineColor="black",
            lineWidth=1.5,
            units="deg",
            autoLog=False,
        )
        half_w = float(width_deg) / 2.0
        half_h = float(height_deg) / 2.0
        self.fragments = []
        for _ in range(int(fragment_count)):
            x1 = rng.uniform(-half_w, half_w)
            y1 = rng.uniform(-half_h, half_h)
            x2 = max(-half_w, min(half_w, x1 + rng.uniform(-1.2, 1.2)))
            y2 = max(-half_h, min(half_h, y1 + rng.uniform(-0.8, 0.8)))
            self.fragments.append(
                visual.Line(
                    win,
                    start=(x1, y1),
                    end=(x2, y2),
                    lineColor="black",
                    lineWidth=float(line_width),
                    units="deg",
                    autoLog=False,
                )
            )

    def draw(self) -> None:
        self.border.draw()
        for fragment in self.fragments:
            fragment.draw()


class ProbeOptionsStim(BaseVisualStim):
    """Post-mask position cue and left/right letter alternatives."""

    def __init__(
        self,
        win,
        *,
        target_position: int,
        left_letter: str,
        right_letter: str,
        slot_x: list[float],
        option_height: float,
        font: str,
    ) -> None:
        super().__init__(win, units="deg", name="probe_options", autoLog=False)
        self.slot_boxes = []
        for index, x in enumerate(slot_x, start=1):
            selected = index == int(target_position)
            self.slot_boxes.append(
                visual.Rect(
                    win,
                    width=0.22,
                    height=0.10 if not selected else 0.22,
                    pos=(float(x), 1.35),
                    fillColor="black" if selected else "#AAAAAA",
                    lineColor="black" if selected else "#AAAAAA",
                    units="deg",
                    autoLog=False,
                )
            )
        self.left = visual.TextStim(
            win,
            text=str(left_letter),
            pos=(-3.0, -0.45),
            height=float(option_height),
            font=str(font),
            color="black",
            units="deg",
            autoLog=False,
        )
        self.right = visual.TextStim(
            win,
            text=str(right_letter),
            pos=(3.0, -0.45),
            height=float(option_height),
            font=str(font),
            color="black",
            units="deg",
            autoLog=False,
        )

    def draw(self) -> None:
        for box in self.slot_boxes:
            box.draw()
        self.left.draw()
        self.right.draw()


def register_word_superiority_stimuli(stim_bank: Any, settings: Any) -> None:
    geometry = dict(settings.perceptual_geometry)

    @stim_bank.define("letter_array")
    def _letter_array_factory(win, display_text="READ", **overrides):
        params = {
            "slot_x": list(geometry["slot_x"]),
            "letter_height": float(geometry["letter_height_deg"]),
            "font": str(geometry["letter_font"]),
        }
        params.update(overrides)
        return LetterArrayStim(win, display_text=str(display_text), **params)

    @stim_bank.define("pattern_mask")
    def _pattern_mask_factory(win, seed=104104, **overrides):
        params = {
            "width_deg": float(geometry["mask_width_deg"]),
            "height_deg": float(geometry["mask_height_deg"]),
            "fragment_count": int(geometry["mask_fragment_count"]),
            "line_width": float(geometry["mask_line_width"]),
        }
        params.update(overrides)
        return PatternMaskStim(win, seed=int(seed), **params)

    @stim_bank.define("probe_options")
    def _probe_factory(win, target_position=1, left_letter="R", right_letter="H", **overrides):
        params = {
            "slot_x": list(geometry["slot_x"]),
            "option_height": float(geometry["probe_letter_height_deg"]),
            "font": str(geometry["letter_font"]),
        }
        params.update(overrides)
        return ProbeOptionsStim(
            win,
            target_position=int(target_position),
            left_letter=str(left_letter),
            right_letter=str(right_letter),
            **params,
        )
