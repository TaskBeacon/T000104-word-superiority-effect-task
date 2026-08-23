# Task Logic Audit

This audit was extracted from Reicher (1969), Wheeler (1970), Johnston and McClelland (1973), and McClelland (1976) before task code was written. It was not reconstructed from an existing task.

## 1. Paradigm Intent

- Task: Reicher-Wheeler Word Superiority Task.
- Primary construct: contextual facilitation of letter identification.
- Manipulated factors: four-letter context type (`word`, `pseudoword`, `illegal_string`, `isolated_letter`) and probed letter position (1-4). The displayed member of a minimally differing pair is balanced as variant A or B.
- Dependent measures: forced-choice letter-identification accuracy and response time, summarized by context and target position. The participant never makes a word/nonword judgment.
- Key citations: Reicher (1969); Wheeler (1970); Johnston & McClelland (1973); McClelland (1976).

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 2 human blocks.
- Trials per block: 32, one occurrence of every context x target-position x displayed-variant label.
- Randomization/counterbalancing: labels are randomized within each block. Each block contains all 32 labels exactly once. The two stimulus matrices for each target position alternate by block, and the left/right placement of the two response alternatives reverses across blocks.
- Condition weight policy: all 32 labels have weight 1 in `task.condition_weights`; runtime resolution is delegated to `TaskSettings.resolve_condition_weights()`.
- Condition generation method: built-in `BlockUnit.generate_conditions(...)`. Simple labels fully represent the core factors, so no custom generator is needed.
- Runtime-generated trial values: `run_trial.py` deterministically realizes the matrix item from target position and block index, and reconstructs the display for the selected context and A/B variant. It does not randomize a core factor. Mask geometry is deterministically seeded from the PsyFlow trial ID and is independent of condition scheduling.

### Trial State Machine

1. `fixation`
   - Onset trigger: `fixation`.
   - Stimuli shown: central black `+` on a white field.
   - Valid keys: none.
   - Timeout behavior: ends after 500 ms.
   - Next state: `brief_display`.
2. `brief_display`
   - Onset trigger: context-specific display trigger.
   - Stimuli shown: a four-slot uppercase word, pronounceable pseudoword, orthographically illegal string, or one isolated target letter in its four-slot position.
   - Valid keys: none.
   - Timeout behavior: ends after 60 ms.
   - Next state: `pattern_mask`.
3. `pattern_mask`
   - Onset trigger: `pattern_mask`.
   - Stimuli shown: a high-contrast rectangular field of program-generated jagged line fragments occupying the four-letter display region.
   - Valid keys: none.
   - Timeout behavior: ends after 200 ms.
   - Next state: `letter_probe`.
4. `letter_probe`
   - Onset trigger: `letter_probe`.
   - Stimuli shown: four position markers with the tested position highlighted, plus two letters arranged left and right. Both alternatives preserve the context category of the paired stimulus.
   - Valid keys: `f` for the left alternative and `j` for the right alternative.
   - Timeout behavior: after 2500 ms, record omission and continue without feedback.
   - Next state: `iti`.
5. `iti`
   - Onset trigger: `iti`.
   - Stimuli shown: central fixation.
   - Valid keys: none.
   - Timeout behavior: ends after 500 ms.
   - Next state: next trial or block break.

## 3. Condition Semantics

- `word_p{1-4}_{a|b}`: a common four-letter English word; A/B identifies which member of a one-letter-different word pair is displayed.
- `pseudoword_p{1-4}_{a|b}`: a pronounceable, orthographically regular four-letter nonword pair matched at the probed position.
- `illegal_string_p{1-4}_{a|b}`: an unpronounceable four-letter string with uncommon/illegal clusters, paired by one probed letter.
- `isolated_letter_p{1-4}_{a|b}`: only the critical letter is visible in the appropriate one of four spatial slots; the other slots are blank.
- Participant-facing text source: static instructions and prompts are defined in `config/*.yaml`; dynamic letters come from the documented item matrices in `task.item_matrices` and are drawn by task-specific PsychoPy primitives.
- Auditability: every condition token decomposes into the three explicit scheduled factors (context, position, displayed pair member); item realization is deterministic by block.
- Localization strategy: instruction/prompt/break text can be replaced in YAML without editing trial code. Letter materials remain English by design because the baseline paradigm tests English orthographic context.

## 4. Response and Scoring Rules

- Response mapping: `f` selects the left alternative; `j` selects the right alternative.
- Response key source: `task.response_keys` in configuration.
- Missing-response policy: timeout is recorded as `omission`; no corrective feedback is shown.
- Correctness logic: correct when the chosen side contains the critical letter that appeared at the probed position.
- Reward/penalty updates: none.
- Running metrics: block breaks report completion only, not accuracy, to avoid changing response strategy. Final data support accuracy and RT by context and position.

## 5. Stimulus Layout Plan

- Screen name: `brief_display`.
  - Stimulus IDs shown together: `letter_array`.
  - Layout anchors: four fixed horizontal slots centered at x = -0.525, -0.175, 0.175, 0.525 deg; y = 0.
  - Size/spacing: uppercase monospaced letters, 0.42 deg high; 0.35 deg center-to-center spacing, yielding an approximately 1.4 deg-wide array.
  - Readability/overlap checks: fixed slots prevent kerning or leading-space shifts; all four contexts occupy the identical spatial envelope.
  - Rationale: equates position and overall array geometry while permitting the isolated-letter control.
- Screen name: `letter_probe`.
  - Stimulus IDs shown together: `probe_prompt`, `probe_options`.
  - Layout anchors: prompt at (0, 3.2); four position markers at y = 1.4; alternatives at (-3.0, -0.3) and (3.0, -0.3).
  - Size/spacing: prompt height 0.55 deg with wrap width 22 deg; alternatives 1.5 deg high; marker spacing matches display slots.
  - Readability/overlap checks: prompt, position row, and choices occupy separate vertical bands; option centers are 6 deg apart.
  - Rationale: makes the tested position explicit only after the masked display, while preserving a simple left/right forced choice.
- Screen name: instruction/break/good-bye.
  - Stimulus IDs shown together: one YAML-defined text stimulus per screen.
  - Layout anchors: centered at (0, 0).
  - Size/spacing: 0.62 deg height, wrap width 24 deg.
  - Readability/overlap checks: single text box only.

## 6. Trigger Plan

- `experiment_start` 1; `instruction` 5; `block_start` 10.
- `fixation` 20.
- `display_word` 31; `display_pseudoword` 32; `display_illegal_string` 33; `display_isolated_letter` 34.
- `pattern_mask` 40; `letter_probe` 50.
- `response_left` 61; `response_right` 62; `response_timeout` 63.
- `iti` 70; `block_end` 90; `experiment_end` 99.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one simple mode-aware orchestration path.
- `utils.py` used: yes, only for strict condition decoding, deterministic item realization, probe-side mapping, and summary helpers.
- Custom stimulus module used: yes, to draw fixed-position letter arrays, the patterned mask, and the post-mask probe without manual draw/flip loops in `run_trial.py`.
- Custom controller used: no; the baseline uses fixed exposure rather than a threshold staircase.
- Legacy/backward-compatibility fallback logic required: no.

## 8. Inference Log

- Decision: 60 ms fixed display duration.
  - Why inference was required: classic experiments individualized exposure to approximately 75% performance, with reported thresholds often around 27-32 ms; a fixed baseline is needed for a portable first release without experimenter-controlled calibration.
  - Citation-supported rationale: Johnston & McClelland (1973), Method/Design and Masking; Wheeler (1970), Procedure. The value is adapted upward for ordinary 60/120 Hz displays and remains tachistoscopic.
- Decision: 200 ms visible patterned-mask interval.
  - Why inference was required: classic apparatus often kept the patterned field present until alternatives were viewed outside the tachistoscope; a browser/local portable sequence needs an explicit mask interval.
  - Citation-supported rationale: Johnston & McClelland (1973) showed the effect depended on a patterned postexposure field; McClelland (1976) used the same patterned-mask conditions.
- Decision: 2500 ms forced-choice deadline and 500 ms ITI.
  - Why inference was required: classic reports emphasized accuracy and self-paced responding rather than a fixed computerized deadline.
  - Citation-supported rationale: Wheeler (1970) emphasized accuracy and comfortable responding; the deadline is a conservative modern implementation choice.
- Decision: two 32-trial blocks.
  - Why inference was required: classic protocols used hundreds of trials and individual threshold blocks; the first TaskBeacon release prioritizes a balanced, practical behavioral session.
  - Citation-supported rationale: every context, critical position, and displayed alternative remains exactly balanced, preserving the core forced-choice contrast.
