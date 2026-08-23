from __future__ import annotations

from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import probe_layout, realize_trial


def _set_context(
    unit: StimUnit,
    *,
    trial_id: int,
    block_id: str,
    condition_id: str,
    phase: str,
    deadline_s: float,
    valid_keys: list[str],
    factors: dict[str, Any],
    stim_id: str,
) -> None:
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=float(deadline_s),
        valid_keys=list(valid_keys),
        block_id=block_id,
        condition_id=condition_id,
        task_factors={**factors, "stage": phase},
        stim_id=stim_id,
    )


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    condition_id = str(condition)
    block_index = int(block_idx or 0)
    trial_id = int(next_trial_id())
    block_name = str(block_id or "block_0")
    spec = realize_trial(condition_id, dict(settings.item_matrices), block_index)
    response_keys = dict(settings.response_keys)
    left_key = str(response_keys["left"])
    right_key = str(response_keys["right"])
    probe = probe_layout(spec, block_index, left_key, right_key)

    factors = {
        "context": spec.context,
        "target_position": spec.target_position,
        "displayed_variant": spec.displayed_variant,
        "pair_id": spec.pair_id,
        "display_text": spec.display_text.replace("|", ""),
        "target_letter": spec.target_letter,
        "alternate_letter": spec.alternate_letter,
        "left_letter": probe["left_letter"],
        "right_letter": probe["right_letter"],
        "correct_key": probe["correct_key"],
        "block_idx": block_index,
    }
    data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_name,
        "block_idx": block_index,
        "condition": condition_id,
        "condition_id": condition_id,
        **factors,
    }

    fixation_duration = float(settings.fixation_duration)
    fixation = StimUnit("fixation", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("fixation"))
    _set_context(
        fixation,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="fixation",
        deadline_s=fixation_duration,
        valid_keys=[],
        factors=factors,
        stim_id="fixation",
    )
    fixation.show(duration=fixation_duration, onset_trigger=settings.triggers.get("fixation")).to_dict(data)

    display_stim = stim_bank.rebuild("letter_array", display_text=spec.display_text)
    display_duration = float(settings.display_duration)
    brief_display = StimUnit("brief_display", win, kb, runtime=trigger_runtime).add_stim(display_stim)
    _set_context(
        brief_display,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="brief_display",
        deadline_s=display_duration,
        valid_keys=[],
        factors=factors,
        stim_id=f"letter_array_{spec.context}",
    )
    brief_display.show(
        duration=display_duration,
        onset_trigger=settings.triggers.get(f"display_{spec.context}"),
    ).to_dict(data)

    mask_duration = float(settings.mask_duration)
    mask_seed = int(settings.overall_seed) + trial_id * 1009
    mask_stim = stim_bank.rebuild("pattern_mask", seed=mask_seed)
    mask = StimUnit("pattern_mask", win, kb, runtime=trigger_runtime).add_stim(mask_stim)
    _set_context(
        mask,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="pattern_mask",
        deadline_s=mask_duration,
        valid_keys=[],
        factors={**factors, "mask_seed": mask_seed},
        stim_id="pattern_mask",
    )
    mask.show(duration=mask_duration, onset_trigger=settings.triggers.get("pattern_mask")).to_dict(data)

    probe_duration = float(settings.probe_duration)
    probe_stim = stim_bank.rebuild(
        "probe_options",
        target_position=spec.target_position,
        left_letter=probe["left_letter"],
        right_letter=probe["right_letter"],
    )
    letter_probe = StimUnit("letter_probe", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("probe_prompt"), probe_stim
    )
    _set_context(
        letter_probe,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="letter_probe",
        deadline_s=probe_duration,
        valid_keys=[left_key, right_key],
        factors=factors,
        stim_id="probe_prompt+probe_options",
    )
    letter_probe.capture_response(
        keys=[left_key, right_key],
        correct_keys=[probe["correct_key"]],
        duration=probe_duration,
        onset_trigger=settings.triggers.get("letter_probe"),
        response_trigger={
            left_key: settings.triggers.get("response_left"),
            right_key: settings.triggers.get("response_right"),
        },
        timeout_trigger=settings.triggers.get("response_timeout"),
        terminate_on_response=True,
    ).to_dict(data)
    response = letter_probe.get_state("response", None)
    rt = letter_probe.get_state("rt", None)
    data["response"] = response
    data["rt"] = float(rt) if isinstance(rt, (int, float)) else None
    data["correct"] = bool(response == probe["correct_key"])
    data["outcome"] = "omission" if response is None else ("correct" if data["correct"] else "incorrect")

    iti_duration = float(settings.iti_duration)
    iti = StimUnit("iti", win, kb, runtime=trigger_runtime).add_stim(stim_bank.get("fixation"))
    _set_context(
        iti,
        trial_id=trial_id,
        block_id=block_name,
        condition_id=condition_id,
        phase="iti",
        deadline_s=iti_duration,
        valid_keys=[],
        factors={**factors, "outcome": data["outcome"]},
        stim_id="fixation",
    )
    iti.show(duration=iti_duration, onset_trigger=settings.triggers.get("iti")).to_dict(data)
    return data
