from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    reset_trial_counter,
    runtime_context,
)

from src import register_word_superiority_stimuli, run_trial, summarize_trials


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def run(options) -> None:
    task_root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir, scope, context = None, nullcontext(), None
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=task_root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": "qa"}
        elif options.mode == "sim":
            subject = {"subject_id": str(context.session.participant_id or "sim")}
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            settings.save_path = str(output_dir)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        settings.triggers = config["trigger_config"]
        trigger_runtime = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(config)
        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, config["stim_config"])
        register_word_superiority_stimuli(stim_bank, settings)
        stim_bank.preload_all()
        settings.save_to_json()
        reset_trial_counter()

        trigger_runtime.send(settings.triggers.get("experiment_start"))
        trigger_runtime.send(settings.triggers.get("instruction"))
        StimUnit("instruction", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get("instruction")
        ).wait_and_continue()

        all_rows: list[dict] = []
        condition_labels = [str(label) for label in settings.conditions]
        condition_weights = settings.resolve_condition_weights()
        for block_index in range(int(settings.total_blocks)):
            block_id = f"block_{block_index + 1}"
            block = (
                BlockUnit(
                    block_id=block_id,
                    block_idx=block_index,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                )
                .generate_conditions(condition_labels=condition_labels, weights=condition_weights, order="random")
                .on_start(lambda _: trigger_runtime.send(settings.triggers.get("block_start")))
                .on_end(lambda _: trigger_runtime.send(settings.triggers.get("block_end")))
                .run_trial(
                    partial(
                        run_trial,
                        stim_bank=stim_bank,
                        trigger_runtime=trigger_runtime,
                        block_id=block_id,
                        block_idx=block_index,
                    )
                )
            )
            block.to_dict(all_rows)
            if block_index < int(settings.total_blocks) - 1:
                StimUnit("block_break", win, kb, runtime=trigger_runtime).add_stim(
                    stim_bank.get_and_format(
                        "block_break",
                        block_number=block_index + 1,
                        total_blocks=int(settings.total_blocks),
                    )
                ).wait_and_continue()

        summary = summarize_trials(all_rows)
        StimUnit("good_bye", win, kb, runtime=trigger_runtime).add_stim(
            stim_bank.get_and_format("good_bye", trial_count=summary["trial_count"])
        ).wait_and_continue(terminate=True)
        trigger_runtime.send(settings.triggers.get("experiment_end"))

        pd.DataFrame(all_rows).to_csv(settings.res_file, index=False)
        trigger_runtime.close()
        core.quit()


def main() -> None:
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Reicher-Wheeler Word Superiority Task.",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()
