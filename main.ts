#!/usr/bin/env node
/**
 * GTA VI Twitch CCU forecast — initial offline implementation.
 * No network access, external packages, or random numbers.
 *
 * NOTE: This is a provisional baseline. Validate field names and output
 * contract against the official Make.fun kit before treating it as final.
 */
const fs = require("node:fs");
const path = require("node:path");

const INPUT_DIR = process.env.MAKEFUN_INPUT_DIR || "/input";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const HORIZON = 23;
const QUANTILES = [0.05, 0.25, 0.50, 0.75, 0.95];

function finite(x) { const n = Number(x); return Number.isFinite(n) ? n : null; }
function median(values) {
  const a = values.filter(Number.isFinite).sort((x,y)=>x-y);
  if (!a.length) return null;
  const m = Math.floor(a.length/2);
  return a.length%2 ? a[m] : (a[m-1]+a[m])/2;
}
function quantile(values, p) {
  const a = values.filter(Number.isFinite).sort((x,y)=>x-y);
  if (!a.length) return null;
  const x=(a.length-1)*p, lo=Math.floor(x), hi=Math.ceil(x);
  return a[lo]+(a[hi]-a[lo])*(x-lo);
}
function getKnown(input) {
  const k=input.known;
  if (Array.isArray(k)) return k[k.length-1] || {};
  return k || input.latest || input.observation || {};
}
function viewers(row) {
  return finite(row && (row.viewers ?? row.ccu ?? row.concurrent_viewers ?? row.value));
}
function getComparableSeries(input) {
  const list=input.comparables || input.comparable_launches || input.comps || [];
  return Array.isArray(list) ? list : [];
}
function extractSeries(comp) {
  const rows=comp.hourly || comp.history_hourly || comp.observations || comp.data || [];
  if (!Array.isArray(rows)) return [];
  return rows.map((r,i)=>({hour:finite(r.hour ?? r.h ?? i), value:viewers(r)}))
    .filter(r=>r.hour!==null && r.value!==null && r.value>0);
}
function forecast(input) {
  const known=getKnown(input);
  const anchor=Math.max(1, viewers(known) ?? finite(input.current_viewers) ?? 1);
  const comps=getComparableSeries(input).map(extractSeries).filter(s=>s.length);
  const historical=input.history_hourly || input.history || [];
  const hist=Array.isArray(historical) ? historical.map(viewers).filter(v=>v!==null && v>0) : [];
  const recent=hist.slice(-6);
  const trend=recent.length>=2
    ? Math.max(-0.18,Math.min(0.18,Math.log(recent[recent.length-1]/recent[0])/Math.max(1,recent.length-1)))
    : 0;
  const rows=[];
  for(let h=1;h<=HORIZON;h++) {
    const ratios=[];
    for(const series of comps) {
      const point=series.find(p=>p.hour===h || p.hour===h+1);
      const base=series.find(p=>p.hour===0 || p.hour===1) || series[0];
      if(point && base && base.value>0) ratios.push(Math.log(point.value/base.value));
    }
    let logRatio=ratios.length ? median(ratios) : -0.012*h;
    if (!Number.isFinite(logRatio)) logRatio=-0.012*h;
    const center=Math.max(1,Math.min(1e9,anchor*Math.exp(logRatio+trend*Math.exp(-h/8)*h*0.35)));
    const deviations=ratios.map(x=>Math.abs(x-logRatio));
    const spread=Math.max(0.20,Math.min(1.10,0.22+(median(deviations)||0.12)*1.4826+0.012*Math.sqrt(h)));
    const z=[-1.6448536269514722,-0.6744897501960817,0,0.6744897501960817,1.6448536269514722];
    const q=z.map(v=>Math.max(1,Math.min(1e9,center*Math.exp(v*spread))));
    for(let i=1;i<q.length;i++) q[i]=Math.max(q[i],q[i-1]);
    rows.push({hour:h, quantiles:q});
  }
  return {hours:rows};
}
function main() {
  if (!fs.existsSync(INPUT_DIR)) throw new Error("Input directory not found: "+INPUT_DIR);
  fs.mkdirSync(OUTPUT_DIR,{recursive:true});
  const names=fs.readdirSync(INPUT_DIR).filter(n=>n.endsWith(".in")).sort();
  if (!names.length) throw new Error("No .in input files found");
  for(const name of names) {
    const input=JSON.parse(fs.readFileSync(path.join(INPUT_DIR,name),"utf8"));
    const result=forecast(input);
    const out=path.join(OUTPUT_DIR,name.slice(0,-3)+".out");
    fs.writeFileSync(out,JSON.stringify(result)+"\n","utf8");
  }
}
if(require.main===module) {
  try { main(); } catch(err) {
    process.stderr.write(String(err && err.stack || err)+"\n");
    process.exitCode=1;
  }
}
module.exports={forecast,median,quantile};
