# Task Plot Review

## Round 0 - pre-generation checks

- Evidence source: canonical README, `main.py`, `config/config.yaml`, `src/run_trial.py`, `src/stimuli.py`, and literature audit.
- Required rows: Word, Pseudoword, Illegal string, Isolated letter.
- Required order: Fixation -> Brief display -> Pattern mask -> Letter probe -> ITI.
- Required timings: 500 ms -> 60 ms -> 200 ms -> 2500 ms max -> 500 ms.
- Required probe semantics: the marker appears only after the mask; response is letter identification via F/J; no feedback phase.
- Header-safe area and fixed postprocessed branding are required.

## Round 1 - rejected

- Evidence match: pass for four rows, phase order, representative stimuli, timings, masks, and target-position markers.
- Visual/background gate: fail. The raw image uses a dark multicolor gradient instead of a pure white background and blank white header band.
- Response-label gate: fail. Both probe alternatives show `F/J`; the left option must show only `F` and the right option only `J`.
- Layout gate: pass. No overlap and all 20 screen snapshots are readable.
- Revision: keep the exact structure and content; change only the background/header treatment and response-key labels.

## Round 2 - targeted correction required

- Background/header gate: pass. Flat white canvas and blank header-safe band are present.
- Evidence match: pass for rows, phase order, timings, representative strings, mask, probe markers, and F-left/J-right mapping.
- Stimulus fidelity gate: fail only for the isolated-letter brief display. The image shows three dash marks around `R`, but the actual task leaves the other three slots blank.
- Readability/layout gate: pass; no overlap, garbling, or incorrect scale relationships in the diagram.
- Revision: remove only those three dash marks and keep `R` at the third-slot horizontal position; preserve everything else exactly.

## Round 3 - accepted

- Evidence match: pass. Exactly four conditions and five phases per row; order, stimuli, keys, probe positions, and all timing labels match the canonical task.
- Stimulus fidelity: pass. The isolated-letter display contains only `R` at slot 3 with the other slots blank; no feedback or unsupported cue is shown.
- Visual quality: pass. Flat white background, readable labels, balanced rows, thin arrows, consistent screen boxes, and no overlap or garbled text.
- Header/brand: pass after postprocessing. The centered title and `Construct:` subtitle occupy the reserved header, and the borderless TaskBeacon lockup is at top right without overlap.
- README embed: pass. `![Task Flow](task_flow.png)` is the first image under `## 2. Task Flow`.
