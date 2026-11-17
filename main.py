#!/usr/bin/env python3
"""Deterministic, offline Make.fun Twitch CCU forecast (program/v1)."""
import json, math, os, pathlib, statistics, sys
from datetime import datetime

def positive(value):
    try:
        number=float(value)
        return number if math.isfinite(number) and number>0 else None
    except (TypeError,ValueError):
        return None

def median(values, default):
    clean=sorted(x for x in values if x is not None and math.isfinite(x) and x>0)
    if not clean: return default
    middle=len(clean)//2
    return clean[middle] if len(clean)%2 else (clean[middle-1]+clean[middle])/2

def timestamp(value):
    try:
        parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
        return parsed.timestamp() if parsed.tzinfo is not None else None
    except (ValueError,TypeError,AttributeError):
        return None

def validate_case(case):
    if not isinstance(case,dict): raise ValueError("case must be a JSON object")
    known=case.get("known")
    try:
        known_viewers=float(known.get("viewers")) if isinstance(known,dict) else float("nan")
    except (TypeError,ValueError):
        known_viewers=float("nan")
    if not math.isfinite(known_viewers) or known_viewers<0:
        raise ValueError("known.viewers must be a finite non-negative number")
    forecast_rows=case.get("forecast")
    if not isinstance(forecast_rows,list) or len(forecast_rows)!=23:
        raise ValueError("forecast must contain exactly 23 rows")
    hours=[]
    for row in forecast_rows:
        if not isinstance(row,dict) or isinstance(row.get("hour"),bool):
            raise ValueError("each forecast row must contain an integer hour")
        hour=row.get("hour")
        if not isinstance(hour,int) or hour<2 or hour>24:
            raise ValueError("forecast hours must be integers from 2 to 24")
        hours.append(hour)
    if sorted(hours)!=list(range(2,25)):
        raise ValueError("forecast must contain each hour from 2 to 24 exactly once")
    for field in ("history","history_hourly","comparables"):
        if case.get(field) is not None and not isinstance(case[field],list):
            raise ValueError(field+" must be an array or null")
    if case.get("streams") is not None and not isinstance(case["streams"],list):
        raise ValueError("streams must be an array or null")

def comparable_profiles(case):
    profiles=[]
    for comparable in case.get("comparables") or []:
        if not isinstance(comparable,dict): continue
        unlock=timestamp(comparable.get("unlock"))
        if unlock is None: continue
        values={}
        for point in comparable.get("hourly") or []:
            if not isinstance(point,dict): continue
            instant=timestamp(point.get("from")); viewers=positive(point.get("viewers"))
            if instant is not None and viewers is not None:
                hour=math.floor((instant-unlock)/3600)
                if -24<=hour<=72: values[hour]=viewers
        base=values.get(0) or median([v for h,v in values.items() if 0<=h<=2],None)
        if base:
            profiles.append({h:max(.03,min(30.0,v/base)) for h,v in values.items()})
    return profiles

def forecast(case):
    validate_case(case)
    known=case["known"]
    first=positive(known.get("viewers")) or 1.0
    channels=positive(known.get("channels"))
    streams=case.get("streams") or []
    top=sum(positive(s.get("viewers")) or 0 for s in streams if isinstance(s,dict))
    share=min(.95,top/first)
    analogues=comparable_profiles(case)
    rows=[]
    for item in case["forecast"]:
        hour=item["hour"]; rel=hour-1; ratios=[]
        for profile in analogues:
            if rel in profile: ratios.append(profile[rel])
            elif profile and rel>max(profile):
                last=max(profile)
                ratios.append(max(.08,profile[last])*math.exp(-.055*(rel-last)))
        ratio=median(ratios,math.exp(-.035*max(0,rel-1)))
        if len(ratios)>=3: ratio=.78*ratio+.22*math.exp(-.025*max(0,rel-1))
        ratio=max(.04,min(12.0,ratio)); center=max(1.0,first*ratio)
        logs=[math.log(max(1.0,first*x)) for x in ratios]
        dispersion=statistics.pstdev(logs) if len(logs)>1 else 0.0
        spread=min(1.05,.22+.018*rel+.35*dispersion)
        if channels: spread+=min(.10,.04/math.sqrt(channels))
        if share>.75: spread+=.025
        qs=[round(max(1.0,min(1_000_000_000.0,center*math.exp(z*spread))),4)
            for z in (-1.645,-.674,0.0,.674,1.645)]
        for i in range(1,5): qs[i]=max(qs[i],qs[i-1])
        rows.append({"hour":hour,"q":qs})
    return {"hours":sorted(rows,key=lambda row:row["hour"])}

def main():
    input_dir=pathlib.Path(os.environ.get("MAKEFUN_INPUT_DIR","/input"))
    output_dir=pathlib.Path(os.environ.get("MAKEFUN_OUTPUT_DIR","/output"))
    output_dir.mkdir(parents=True,exist_ok=True)
    files=sorted(input_dir.glob("*.in"),key=lambda path:path.name)
    if not files: raise RuntimeError("No .in case files in "+str(input_dir))
    for source in files:
        case=json.loads(source.read_text(encoding="utf-8"))
        result=forecast(case)
        encoded=json.dumps(result,ensure_ascii=False,separators=(",",":"),allow_nan=False)
        if len(encoded.encode("utf-8"))>65536: raise RuntimeError("Output too large")
        (output_dir/(source.stem+".out")).write_text(encoded,encoding="utf-8")

if __name__=="__main__":
    try: main()
    except Exception as error:
        print("forecast error: "+str(error),file=sys.stderr)
        raise
