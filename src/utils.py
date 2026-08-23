from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


CONTEXTS = ("word", "pseudoword", "illegal_string", "isolated_letter")


@dataclass(frozen=True)
class ConditionSpec:
    context: str
    target_position: int
    displayed_variant: str


@dataclass(frozen=True)
class TrialSpec:
    condition_id: str
    context: str
    target_position: int
    displayed_variant: str
    pair_id: str
    display_text: str
    option_a: str
    option_b: str
    target_letter: str
    alternate_letter: str


def decode_condition(condition: str) -> ConditionSpec:
    token = str(condition)
    for context in CONTEXTS:
        prefix = f"{context}_p"
        if token.startswith(prefix):
            remainder = token[len(prefix) :]
            try:
                position_text, variant = remainder.split("_", 1)
                position = int(position_text)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid condition token: {token}") from exc
            if position not in (1, 2, 3, 4) or variant not in ("a", "b"):
                raise ValueError(f"Invalid condition token: {token}")
            return ConditionSpec(context=context, target_position=position, displayed_variant=variant)
    raise ValueError(f"Unknown condition token: {token}")


def _matrix_for_position(item_matrices: dict[str, Any], target_position: int, block_idx: int) -> dict[str, Any]:
    matrices = list(item_matrices[str(target_position)])
    if len(matrices) != 2:
        raise ValueError(f"Position {target_position} must define exactly two item matrices")
    return dict(matrices[int(block_idx) % len(matrices)])


def realize_trial(condition: str, item_matrices: dict[str, Any], block_idx: int) -> TrialSpec:
    spec = decode_condition(condition)
    matrix = _matrix_for_position(item_matrices, spec.target_position, int(block_idx))
    option_a = str(matrix["option_a"]).upper()
    option_b = str(matrix["option_b"]).upper()
    if len(option_a) != 1 or len(option_b) != 1 or option_a == option_b:
        raise ValueError(f"Invalid alternatives in matrix {matrix.get('pair_id')}")

    if spec.context == "isolated_letter":
        target = option_a if spec.displayed_variant == "a" else option_b
        slots = ["", "", "", ""]
        slots[spec.target_position - 1] = target
        display_text = "|".join(slots)
    else:
        pair = list(matrix[spec.context])
        if len(pair) != 2:
            raise ValueError(f"Matrix {matrix.get('pair_id')} has an invalid {spec.context} pair")
        display_text = str(pair[0 if spec.displayed_variant == "a" else 1]).upper()
        if len(display_text) != 4:
            raise ValueError(f"Display must contain four letters: {display_text}")
        expected = option_a if spec.displayed_variant == "a" else option_b
        if display_text[spec.target_position - 1] != expected:
            raise ValueError(f"Critical letter mismatch in matrix {matrix.get('pair_id')}")

    target_letter = option_a if spec.displayed_variant == "a" else option_b
    alternate_letter = option_b if spec.displayed_variant == "a" else option_a
    return TrialSpec(
        condition_id=str(condition),
        context=spec.context,
        target_position=spec.target_position,
        displayed_variant=spec.displayed_variant,
        pair_id=str(matrix["pair_id"]),
        display_text=display_text,
        option_a=option_a,
        option_b=option_b,
        target_letter=target_letter,
        alternate_letter=alternate_letter,
    )


def probe_layout(spec: TrialSpec, block_idx: int, left_key: str, right_key: str) -> dict[str, str]:
    option_a_left = int(block_idx) % 2 == 0
    left_letter = spec.option_a if option_a_left else spec.option_b
    right_letter = spec.option_b if option_a_left else spec.option_a
    correct_key = str(left_key) if spec.target_letter == left_letter else str(right_key)
    return {"left_letter": left_letter, "right_letter": right_letter, "correct_key": correct_key}


def summarize_trials(rows: Iterable[dict[str, Any]]) -> dict[str, float | int]:
    logical_rows = [row for row in rows if row.get("condition")]
    answered = [row for row in logical_rows if row.get("response") is not None]
    correct = [row for row in answered if bool(row.get("correct"))]
    return {
        "trial_count": len(logical_rows),
        "answered_count": len(answered),
        "correct_count": len(correct),
        "accuracy": (len(correct) / len(answered)) if answered else 0.0,
    }
