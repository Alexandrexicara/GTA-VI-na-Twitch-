import json, os, pathlib, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import main

def sample_case():
    return {
      "id":"smoke","game":{"name":"Grand Theft Auto VI","twitch_id":"1867279146"},
      "day_start":"2026-11-19T00:00:00Z","checkpoint":"2026-11-19T01:00:00Z",
      "levels":[0.05,0.25,0.5,0.75,0.95],
      "known":[{"hour":1,"from":"2026-11-19T00:00:00Z","until":"2026-11-19T01:00:00Z","viewers":100000,"channels":500,"reads":60}],
      "forecast":[{"hour":h,"from":f"2026-11-19T{h-1:02d}:00:00Z","until":("2026-11-20T00:00:00Z" if h==24 else f"2026-11-19T{h:02d}:00:00Z")} for h in range(2,25)],
      "history":[{"at":"2026-11-18T23:59:00Z","viewers":90000,"channels":400}],
      "history_hourly":[],"streams":[{"login":"sample","viewers":12000,"language":"en","started_at":"2026-11-19T00:10:00Z"}],
      "categories_hourly":[],
      "comparables":[{"name":"Synthetic launch","day_start":"2026-01-01T00:00:00Z","unlock":"Midnight local release; descriptive text, not a timestamp","platforms":["console"],"source":"synthetic test only",
        "hourly":[{"from":f"2026-01-01T{h:02d}:00:00Z","viewers":max(1000,10000-h*200),"channels":100} for h in range(25)]}],
      "notes":["Synthetic test fixture; not an official practice case."]
    }

class ForecastTests(unittest.TestCase):
    def test_output_contract_and_quantiles(self):
        result=main.forecast(sample_case())
        self.assertEqual(set(result),{"hours"})
        self.assertEqual([r["hour"] for r in result["hours"]],list(range(2,25)))
        for row in result["hours"]:
            self.assertEqual(set(row),{"hour","q"})
            self.assertEqual(len(row["q"]),5)
            self.assertTrue(all(0<q<=1_000_000_000 for q in row["q"]))
            self.assertEqual(row["q"],sorted(row["q"]))
    def test_deterministic(self):
        case=sample_case()
        self.assertEqual(main.forecast(case),main.forecast(case))
    def test_accepts_legacy_object_known(self):
        case=sample_case(); case["known"]=case["known"][0]
        self.assertEqual(len(main.forecast(case)["hours"]),23)
    def test_accepts_zero_first_hour_count(self):
        case=sample_case(); case["known"][0]["viewers"]=0
        result=main.forecast(case)
        self.assertEqual(len(result["hours"]),23)
        self.assertTrue(all(all(q>0 for q in row["q"]) for row in result["hours"]))
    def test_rejects_missing_hour(self):
        case=sample_case(); case["forecast"]=case["forecast"][:-1]
        with self.assertRaises(ValueError): main.forecast(case)
    def test_rejects_duplicate_hour(self):
        case=sample_case(); case["forecast"][-1]["hour"]=23
        with self.assertRaises(ValueError): main.forecast(case)
    def test_cli_processes_all_input_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp); src=base/"in"; dst=base/"out"; src.mkdir()
            (src/"b.in").write_text(json.dumps(sample_case()),encoding="utf-8")
            (src/"a.in").write_text(json.dumps(sample_case()),encoding="utf-8")
            env=dict(os.environ,MAKEFUN_INPUT_DIR=str(src),MAKEFUN_OUTPUT_DIR=str(dst))
            subprocess.run([sys.executable,str(ROOT/"main.py")],check=True,env=env,timeout=8)
            self.assertEqual(sorted(p.name for p in dst.glob("*.out")),["a.out","b.out"])
            self.assertEqual(len(json.loads((dst/"a.out").read_text())["hours"]),23)

if __name__=="__main__": unittest.main()
