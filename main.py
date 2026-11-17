#!/usr/bin/env python3
"""Deterministic, offline Make.fun Twitch CCU forecast."""
import json, math, os, pathlib, statistics, sys
from datetime import datetime

def positive(x):
    try:
        n=float(x)
        return n if math.isfinite(n) and n>0 else None
    except (TypeError,ValueError):
        return None

def med(xs, default):
    a=sorted(x for x in xs if x is not None and math.isfinite(x) and x>0)
    if not a: return default
    m=len(a)//2
    return a[m] if len(a)%2 else (a[m-1]+a[m])/2

def stamp(s):
    try: return datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except (ValueError,TypeError,AttributeError): return None

def profiles(case):
    out=[]
    for c in case.get("comparables") or []:
        unlock=stamp(c.get("unlock"))
        if unlock is None: continue
        vals={}
        for r in c.get("hourly") or []:
            t=stamp(r.get("from")); v=positive(r.get("viewers"))
            if t is not None and v is not None:
                k=math.floor((t-unlock)/3600)
                if -24<=k<=72: vals[k]=v
        base=vals.get(0) or med([v for k,v in vals.items() if 0<=k<=2],None)
        if base:
            out.append({k:max(.03,min(30,v/base)) for k,v in vals.items()})
    return out

def forecast(case):
    first=positive((case.get("known") or {}).get("viewers")) or 1.0
    channels=positive((case.get("known") or {}).get("channels"))
    streams=case.get("streams") or []
    top=sum(positive(s.get("viewers")) or 0 for s in streams)
    share=min(.95,top/first)
    analogs=profiles(case)
    rows=[]
    for item in case.get("forecast") or []:
        h=int(item["hour"]); rel=h-1
        ratios=[]
        for p in analogs:
            if rel in p: ratios.append(p[rel])
            elif p and rel>max(p):
                ratios.append(max(.08,p[max(p)])*math.exp(-.055*(rel-max(p))))
        ratio=med(ratios,math.exp(-.035*max(0,rel-1)))
        if len(ratios)>=3: ratio=.78*ratio+.22*math.exp(-.025*max(0,rel-1))
        ratio=max(.04,min(12,ratio))
        center=max(1,first*ratio)
        dispersion=statistics.pstdev([math.log(max(1,first*x)) for x in ratios]) if len(ratios)>1 else 0
        spread=min(1.05,.22+.018*rel+.35*dispersion)
        if channels: spread+=min(.10,.04/math.sqrt(channels))
        if share>.75: spread+=.025
        qs=[center*math.exp(z*spread) for z in (-1.645,-.674,0,.674,1.645)]
        qs=[round(max(1,min(1e9,x)),4) for x in qs]
        for i in range(1,5): qs[i]=max(qs[i],qs[i-1])
        rows.append({"hour":h,"q":qs})
    by={r["hour"]:r for r in rows}
    return {"hours":[by[h] for h in range(2,25)]}

def main():
    srcdir=pathlib.Path(os.environ.get("MAKEFUN_INPUT_DIR","/input"))
    outdir=pathlib.Path(os.environ.get("MAKEFUN_OUTPUT_DIR","/output"))
    outdir.mkdir(parents=True,exist_ok=True)
    files=sorted(srcdir.glob("*.in"),key=lambda p:p.name)
    if not files: raise RuntimeError("No .in case files in "+str(srcdir))
    for src in files:
        case=json.loads(src.read_text(encoding="utf-8"))
        result=forecast(case)
        data=json.dumps(result,ensure_ascii=False,separators=(",",":"),allow_nan=False)
        if len(data.encode("utf-8"))>65536: raise RuntimeError("Output too large")
        (outdir/(src.stem+".out")).write_text(data,encoding="utf-8")

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("forecast error: "+str(e),file=sys.stderr)
        raise
