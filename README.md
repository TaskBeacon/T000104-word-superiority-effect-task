# Reicher-Wheeler Word Superiority Task

| Field | Value |
|---|---|
| Name | Reicher-Wheeler Word Superiority Task |
| Version | v0.1.0 |
| URL / Repository | https://github.com/TaskBeacon/T000104-word-superiority-effect-task |
| Short Description | Masked two-alternative letter identification across word, pseudoword, illegal-string, and isolated-letter contexts |
| Created By | TaskBeacon |
| Date Updated | 2026-08-24 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 or compatible |
| Modality | Behavior |
| Language | English |
| Voice Name | en-US-GuyNeural (configured; voice disabled) |

## 1. Task Overview

This task measures whether a meaningful or orthographically familiar context improves identification of a briefly presented letter. Participants see a four-letter English word, a pronounceable pseudoword, an illegal letter string, or one isolated letter. After a patterned mask, they choose which of two letters appeared at a probed position.

The response is always a **letter-identification** response. Participants never judge whether the display is a word, so this is not a lexical-decision task.

Primary outcomes are forced-choice accuracy and reaction time by context and target position. The canonical contrast is higher letter-identification accuracy for letters embedded in words than for letters embedded in illegal strings or shown alone; the pseudoword condition tests facilitation from regular orthographic structure.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

The human profile contains two blocks of 32 trials. Each block contains every combination of four contexts, four target positions, and two displayed members of the paired stimulus exactly once. Trial order is randomized. The second block uses the alternate item matrix for each position and reverses the left/right placement of each letter pair.

### Trial-Level Flow

1. Fixation (`500 ms`).
2. Four-slot display (`60 ms`): word, pseudoword, illegal string, or isolated letter.
3. High-contrast program-generated patterned mask (`200 ms`).
4. Post-mask position cue and two letter alternatives (`2500 ms` maximum): `F` selects the left letter and `J` selects the right letter.
5. Fixation ITI (`500 ms`).

No trial-by-trial feedback is shown. Participants are instructed to prioritize accuracy and guess when unsure.

### Controller Logic

There is no adaptive controller in the baseline release. The classic studies used individual threshold calibration; this portable version uses a documented fixed 60 ms exposure. Condition scheduling uses PsyFlow's balanced `BlockUnit.generate_conditions(...)` path.

### Other logic

The program-generated line-fragment mask is seeded independently from condition scheduling. Item realization is deterministic from target position and block index, and left/right alternative placement reverses across blocks.

## 3. Configuration Summary

### a. Subject Info

| Field | Human profile |
|---|---|
| Participant ID | Three digits, 101-999 |
| Age | 18-80 years |

### b. Window Settings

| Parameter | Value |
|---|---|
| Resolution | 1280 x 800 |
| Units | degrees of visual angle |
| Background | white |
| Monitor geometry | 35.5 cm width at 57 cm |

### c. Stimuli

| Component | Implementation |
|---|---|
| Letter array | Four fixed Courier New slots, approximately 1.4 deg total width and 0.42 deg letter height |
| Contexts | word, pronounceable pseudoword, illegal string, isolated letter |
| Mask | 3.4 x 1.8 deg white field with 72 black jagged line fragments |
| Probe | Four position markers plus two spatially separated letter alternatives |
| Materials | Eight minimally differing item matrices; common words checked against the open `wordfreq` frequency table |

### d. Timing

| Phase | Duration |
|---|---:|
| Fixation | 500 ms |
| Brief display | 60 ms |
| Pattern mask | 200 ms |
| Letter probe | 2500 ms maximum |
| ITI | 500 ms |

### Triggers

| Event | Code(s) |
|---|---|
| Experiment / block lifecycle | 1, 5, 10, 90, 99 |
| Fixation | 20 |
| Display contexts | 31-34 |
| Pattern mask / probe | 40, 50 |
| Left / right / timeout | 61, 62, 63 |
| ITI | 70 |

### Adaptive controller

None. The fixed-duration baseline is intentionally explicit; a threshold-calibrated variant can be added separately without changing this task's analysis contract.

## 4. Methods (for academic publication)

Participants completed a computerized Reicher-Wheeler forced-choice letter-identification task. Each trial began with a 500 ms fixation. A four-slot display was then presented for 60 ms and contained a four-letter English word, a pronounceable pseudoword, an orthographically illegal string, or a single critical letter in one of the four spatial positions. The display was immediately followed by a 200 ms high-contrast patterned mask generated from irregular black line fragments. A post-mask probe then indicated one of the four positions and displayed two letter alternatives. Participants selected the left alternative with `F` or the right alternative with `J` within 2500 ms. The alternatives differed only at the critical position and were constructed to preserve the stimulus category of the paired displays, limiting contextual guessing. No accuracy feedback was provided.

The design crossed context (word, pseudoword, illegal string, isolated letter), target position (1-4), and displayed pair member (A/B). Each of two blocks contained all 32 combinations once in randomized order. Pair-side placement reversed across blocks. Primary analyses compare letter-identification accuracy and response time across context types, with target position available as a balanced factor.

The implementation follows the forced-choice logic of Reicher (1969) and Wheeler (1970), the patterned-mask controls and visual geometry of Johnston and McClelland (1973), and the explicit separation of words, pseudowords, and unrelated strings in McClelland (1976). Fixed display, mask, probe, and ITI durations are documented adaptations for a portable first release.

### Run

```powershell
python main.py human
python main.py qa --config config/config_qa.yaml
python main.py sim --config config/config_scripted_sim.yaml
python main.py sim --config config/config_sampler_sim.yaml
```

See `references/parameter_mapping.md`, `references/stimulus_mapping.md`, and `references/task_logic_audit.md` for evidence-to-code traceability.
