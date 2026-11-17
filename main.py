#!/usr/bin/env python3
"""Deterministic, offline Make.fun Twitch CCU forecast (program/v1)."""
import json, math, os, pathlib, sys
from datetime import datetime

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
NORMAL_Z = (-1.645, -0.674, 0.0, 0.674, 1.645)
SIMILARITY_BANDWIDTH = 0.75

def positive(value):
    try:
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (TypeError, ValueError):
        return None

def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.timestamp() if parsed.tzinfo is not None else None
    except (ValueError, TypeError, AttributeError):
        return None

def known_row(case):
    known = case.get("known")
    if isinstance(known, list):
        if len(known) != 1:
            raise ValueError("known must contain exactly one hour-1 row")
        known = known[0]
    if not isinstance(known, dict):
        raise ValueError("known must be an hour-1 object or a one-row array")
    return known

def validate_case(case):
    if not isinstance(case, dict):
        raise ValueError("case must be a JSON object")
    known = known_row(case)
    try:
        known_viewers = float(known.get("viewers"))
    except (TypeError, ValueError):
        known_viewers = float("nan")
    if not math.isfinite(known_viewers) or known_viewers < 0:
        raise ValueError("known.viewers must be a finite non-negative number")
    forecast_rows = case.get("forecast")
    if not isinstance(forecast_rows, list) or len(forecast_rows) != 23:
        raise ValueError("forecast must contain exactly 23 rows")
    hours = []
    for row in forecast_rows:
        if not isinstance(row, dict) or isinstance(row.get("hour"), bool):
            raise ValueError("each forecast row must contain an integer hour")
        hour = row.get("hour")
        if not isinstance(hour, int) or hour < 2 or hour > 24:
            raise ValueError("forecast hours must be integers from 2 to 24")
        hours.append(hour)
    if sorted(hours) != list(range(2, 25)):
        raise ValueError("forecast must contain each hour from 2 to 24 exactly once")
    for field in ("history", "history_hourly", "comparables"):
        if case.get(field) is not None and not isinstance(case[field], list):
            raise ValueError(field + " must be an array or null")
    for field in ("streams", "categories_hourly"):
        if case.get(field) is not None and not isinstance(case[field], list):
            raise ValueError(field + " must be an array or null")

def comparable_profiles(case):
    """Normalize each launch to its UTC release-day first hour.
    The official unlock field is descriptive prose, not a timestamp.
    day_start is the machine-readable UTC anchor for the case.
    """
    profiles = []
    for comparable in case.get("comparables") or []:
        if not isinstance(comparable, dict):
            continue
        name = str(comparable.get("name", "")).lower()
        if "grand theft auto vi category before release" in name:
            continue
        start = timestamp(comparable.get("day_start"))
        if start is None:
            continue
        values = {}
        for point in comparable.get("hourly") or []:
            if not isinstance(point, dict):
                continue
            instant = timestamp(point.get("from"))
            viewers = positive(point.get("viewers"))
            if instant is None or viewers is None:
                continue
            hour = round((instant - start) / 3600.0)
            if -336 <= hour <= 72:
                values[hour] = viewers
        base = values.get(0)
        if base is None:
            early = [values[h] for h in (0, 1, 2) if h in values]
            if early:
                early.sort()
                middle = len(early) // 2
                base = early[middle] if len(early) % 2 else (early[middle - 1] + early[middle]) / 2
        if base is not None and base > 0:
            profiles.append({"base": base, "values": values})
    return profiles

def weighted_quantile(values, weights, quantile):
    pairs = sorted(zip(values, weights), key=lambda pair: pair[0])
    total = sum(weight for _, weight in pairs)
    if not pairs or total <= 0:
        return 0.0
    threshold = quantile * total
    cumulative = 0.0
    for value, weight in pairs:
        cumulative += weight
        if cumulative >= threshold:
            return value
    return pairs[-1][0]

def forecast(case):
    validate_case(case)
    known = known_row(case)
    first = positive(known.get("viewers")) or 1.0
    analogues = comparable_profiles(case)
    rows = []
    for item in case["forecast"]:
        hour = item["hour"]
        rel = hour - 1
        ratios, weights = [], []
        for profile in analogues:
            value = profile["values"].get(rel)
            if value is None:
                continue
            distance = abs(math.log(profile["base"] / first))
            weight = math.exp(-distance / SIMILARITY_BANDWIDTH)
            ratios.append(math.log(max(1.0, value / profile["base"])))
            weights.append(weight)
        qs = []
        for tau, z in zip(LEVELS, NORMAL_Z):
            if ratios:
                empirical = weighted_quantile(ratios, weights, tau)
                log_ratio = 0.96 * empirical + 0.04 * (z * 0.15 * math.sqrt(rel))
            else:
                log_ratio = z * 0.15 * math.sqrt(rel)
            value = first * math.exp(max(-12.0, min(12.0, log_ratio)))
            qs.append(round(max(1.0, min(1_000_000_000.0, value)), 4))
        for index in range(1, 5):
            qs[index] = max(qs[index], qs[index - 1])
        rows.append({"hour": hour, "q": qs})
    return {"hours": sorted(rows, key=lambda row: row["hour"])}

def main():
    input_dir = pathlib.Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = pathlib.Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(input_dir.glob("*.in"), key=lambda path: path.name)
    if not files:
        raise RuntimeError("No .in case files in " + str(input_dir))
    for source in files:
        case = json.loads(source.read_text(encoding="utf-8"))
        result = forecast(case)
        encoded = json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        if len(encoded.encode("utf-8")) > 65536:
            raise RuntimeError("Output too large")
        (output_dir / (source.stem + ".out")).write_text(encoded, encoding="utf-8")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("forecast error: " + str(error), file=sys.stderr)
        raise
