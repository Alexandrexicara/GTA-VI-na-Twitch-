# GTA VI Twitch CCU Forecast

Offline, deterministic Python 3.13 entry for Make.fun's **Forecast GTA VI's launch-day Twitch viewers hour by hour** bounty.

## Competition contract

- Entrypoint: `python3 /bot/main.py` (Python 3.13; standard library only).
- Input: every `*.in` file in `MAKEFUN_INPUT_DIR`, or `/input` by default. Each file is one UTF-8 JSON object using `makefun/twitch-ccu-case/v1`.
- Output: one matching `*.out` file in `MAKEFUN_OUTPUT_DIR`, or `/output` by default.
- Each output is exactly `{"hours":[...]}`: 23 rows for hours 2–24, each with five ordered quantiles (5%, 25%, 50%, 75%, 95%).
- No network calls, dependencies, randomness, or writes outside the output directory.
- The program is designed for the official 8-second / 1-CPU / 1024-MB sandbox.

## Model

The current deterministic baseline normalizes each comparable launch's hourly trajectory to its unlock hour, combines available ratios by median, bounds extrapolation, and widens quantile spread with horizon and observed dispersion. It also uses the first-hour viewer/channel count and top-stream concentration when present.

This is a **baseline, not a proven winning model**. The official four practice cases and sealed final case must be used for model selection and scoring. Do not treat synthetic smoke tests as competition scores.

## Local smoke test

```bash
python3 -m unittest discover -s tests -v
mkdir -p /tmp/gta-input /tmp/gta-output
cp example-case.in /tmp/gta-input/smoke.in
MAKEFUN_INPUT_DIR=/tmp/gta-input MAKEFUN_OUTPUT_DIR=/tmp/gta-output python3 main.py
python3 -c "import json; d=json.load(open('/tmp/gta-output/smoke.out')); assert len(d['hours']) == 23"
```

Official brief: https://make.fun/bounty/gta6-twitch-ccu-forecast-01
