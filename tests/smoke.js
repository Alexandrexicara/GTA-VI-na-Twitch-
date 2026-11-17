const assert = require("node:assert/strict");
const { forecast } = require("../main.ts");
const sample = {
  known: [{ viewers: 100000 }],
  history_hourly: [92000, 95000, 98000, 100000].map(viewers => ({ viewers })),
  comparables: [{ hourly: Array.from({length:25}, (_,hour)=>({hour,viewers:Math.round(100000*Math.exp(-0.01*hour))})) }]
};
const out=forecast(sample);
assert.equal(out.hours.length,23);
assert.equal(out.hours[0].hour,1);
assert.equal(out.hours[22].hour,23);
for (const row of out.hours) {
  assert.equal(row.quantiles.length,5);
  assert(row.quantiles.every(Number.isFinite));
  assert(row.quantiles.every(x=>x>0));
  for(let i=1;i<5;i++) assert(row.quantiles[i]>=row.quantiles[i-1]);
}
console.log("PASS: 23 forecast rows with five finite ordered quantiles each.");
