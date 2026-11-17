import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("forecast", Path(__file__).parents[1] / "main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

case = {
    "known": {"viewers": 100000, "channels": 500},
    "streams": [{"viewers": 20000}, {"viewers": 10000}],
    "comparables": [{
        "unlock": "2026-11-19T00:00:00Z",
        "hourly": [
            {"from": f"2026-11-{19 + i // 24:02d}T{i % 24:02d}:00:00Z", "viewers": 100000 * (0.98 ** i)}
            for i in range(25)
        ],
    }],
    "forecast": [{"hour": h} for h in range(2, 25)],
}
result = module.forecast(case)
assert len(result["hours"]) == 23
assert [row["hour"] for row in result["hours"]] == list(range(2, 25))
for row in result["hours"]:
    assert len(row["q"]) == 5
    assert all(isinstance(x, (int, float)) and x > 0 for x in row["q"])
    assert row["q"] == sorted(row["q"])
print("PASS: 23 hours, five positive ordered quantiles per hour")
