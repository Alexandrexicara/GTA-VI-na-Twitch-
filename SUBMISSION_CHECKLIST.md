# Make.fun submission checklist

Competition: https://make.fun/bounty/gta6-twitch-ccu-forecast-01

## Completed and verified

- [x] Public GitHub repository exists and was created at 2026-11-17 13:18:51 UTC, after the competition opened at 06:00 UTC.
- [x] Repository is public and contains an MIT license file.
- [x] Python entrypoint `main.py` is at the repository root.
- [x] Program uses only the Python standard library, is deterministic, reads all `*.in` files and writes matching `*.out` files.
- [x] Fixed the official input shape: `known` is a one-row array, and comparable `unlock` values are descriptive text; trajectories are anchored to `day_start`.
- [x] Excluded GTA VI's own pre-release category history from the launch-analogue pool.
- [x] Downloaded the official kit and executed all four official inputs: `p00.in`, `p01.in`, `p02.in`, `p03.in`.
- [x] Each official input produced a valid output with exactly 23 rows (hours 2–24), five ordered positive quantiles per row, and all values within the output limit.
- [x] The four-case run completed in under one second in the available Python 3.11 environment.
- [x] All 10 repository unit/CLI tests passed in Python 3.13.5 during the 2026-11-18 review; the updated smoke test also passed.
- [x] Netlify production deployment is ready: https://gta-tuch.netlify.app

## Not yet verified

- [x] Browser baseline correction checked with Node.js 22: comparable alignment uses `day_start`, ignores descriptive `unlock`, and excludes GTA VI pre-release category history. The browser remains a separate experimental baseline and is not the official Python engine.

- [ ] Official Make.fun practice scores. The downloaded practice inputs contain the forecast inputs, but the expected future-hour answers are held by the Make.fun grader. A local run cannot calculate the official practice score.
- [ ] GitHub Actions runner execution. Recent workflow runs ended before any job steps were recorded (zero steps / no runner assigned), so the successful local Python 3.13.5 test run is the available verification; the Actions runner itself remains unverified.
- [ ] Python 3.13 runtime in the exact Make.fun sandbox. Local validation passed on Python 3.13.5, but the exact Make.fun sandbox has not been exercised.
- [ ] The analogue-pool leave-one-out proxy loss was 0.476852. This is an internal cross-validation proxy, not an official Make.fun score and not proof of beating the house baseline.

## Mandatory before a reward-eligible submission

- [ ] Build/revise the entry inside a genuine Make.fun-witnessed session using an accepted harness (for example Codex, Claude Code, Muse app, or Superbot). The existing ChatGPT/GitHub connector edits are not Make.fun-witnessed agent-session transcripts.
- [ ] The recorded session must actually write/revise the submitted code and satisfy the kit's transcript checks. Do not fabricate, edit, borrow, or upload reconstructed transcripts. A ChatGPT account export is not accepted as a substitute.
- [ ] Create the required `makefun-run.json` run record from the actual recorded session, with the real prompt, harness, version, provider, model, effort, MCP servers and instruction-file declarations.
- [ ] Seal the recording with the Make.fun kit CLI and retain the genuine recording ID.
- [ ] Sign the entry message with a Solana wallet linked to the Make.fun account. The bounty's reward is locked in escrow.
- [ ] Submit the public repository URL, full commit SHA, recording ID and wallet signature through the official Make.fun kit CLI before the deadline.

## Important

The source code is prepared and the official kit inputs now run, but no Make.fun entry has been submitted. The remaining transcript and wallet-signing steps cannot be truthfully completed from this ChatGPT conversation: they require the user's accepted Make.fun-recorded agent session and linked Solana wallet. Never share the wallet's seed phrase or private key.
