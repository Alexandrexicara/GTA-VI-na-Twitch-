# GTA VI Twitch CCU Forecast

Offline, deterministic Python 3.13 entry for Make.fun's **Forecast GTA VI's launch-day Twitch viewers hour by hour** bounty.

## Competition contract

- Entrypoint: `python3 /bot/main.py` (Python 3.13; standard library only).
- Input: every `*.in` file in `MAKEFUN_INPUT_DIR`, or `/input` by default. Each file is one UTF-8 JSON object using `makefun/twitch-ccu-case/v1`.
- The official `known` field is a one-row array; the program accepts that format and the earlier object-shaped smoke fixture.
- Comparable launch trajectories are aligned to the machine-readable UTC `day_start` field. The descriptive `unlock` field is prose and is not parsed as a timestamp.
- Output: one matching `*.out` file in `MAKEFUN_OUTPUT_DIR`, or `/output` by default.
- Each output is exactly `{"hours":[...]}`: 23 rows for hours 2–24, each with five ordered quantiles (5%, 25%, 50%, 75%, 95%).
- No network calls, dependencies, randomness, or writes outside the output directory.
- The program is designed for the official 8-second / 1-CPU / 1024-MB sandbox.

## Model

The model uses comparable launches' hour-by-hour viewer ratios relative to their UTC release-day first hour. It excludes the GTA VI category's own pre-release history from the launch-analogue pool, weights analogues by similarity to the observed first-hour audience size, and estimates each quantile from the weighted empirical distribution. A small shrinkage toward the house persistence forecast stabilizes the estimates.

This is a deterministic baseline model, not a guaranteed winning forecast. The Make.fun practice cases are scored on the platform; synthetic tests and leave-one-out checks on the analogue pool are not official competition scores.

## Local smoke test

```bash
python3 -m unittest discover -s tests -v
mkdir -p /tmp/gta-input /tmp/gta-output
cp example-case.in /tmp/gta-input/smoke.in
MAKEFUN_INPUT_DIR=/tmp/gta-input MAKEFUN_OUTPUT_DIR=/tmp/gta-output python3 main.py
python3 -c "import json; d=json.load(open('/tmp/gta-output/smoke.out')); assert len(d['hours']) == 23"
```

Official brief: https://make.fun/bounty/gta6-twitch-ccu-forecast-01
