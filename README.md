# GTA VI Twitch CCU Forecast

Offline and deterministic Make.fun entry. Python 3.13, standard library only.

- Entrypoint: `python3 /bot/main.py`
- Reads all `*.in` files from `MAKEFUN_INPUT_DIR` or `/input`.
- Writes one matching `*.out` file per case to `MAKEFUN_OUTPUT_DIR` or `/output`.
- Produces 23 rows for hours 2–24, each with ordered 5%, 25%, 50%, 75%, and 95% quantiles.

The initial model aligns historical comparable-game hourly trajectories to each game's unlock, uses robust median ratios, bounds extrapolation, and widens uncertainty with forecast horizon. It makes no network calls and uses no third-party packages.

This is an initial baseline, not a verified winning model. It must be tested against the four official practice cases and compared with the house baseline before submission.
