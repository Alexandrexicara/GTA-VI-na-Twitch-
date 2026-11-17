# Make.fun submission checklist

Competition: https://make.fun/bounty/gta6-twitch-ccu-forecast-01

## Repository work
- [x] Public GitHub repository exists.
- [x] Python 3.13 entrypoint at repository root.
- [x] Standard-library-only deterministic program.
- [x] Reads all `*.in` files in filename order and writes matching `*.out` files.
- [x] Output contract validation: 23 hours, hours 2–24, five ordered positive quantiles, maximum 1e9.
- [x] Synthetic case fixture follows the documented `makefun/twitch-ccu-case/v1` structure.
- [x] Unit tests and end-to-end CLI tests added.
- [x] GitHub Actions workflow added for Python 3.13.
- [x] Browser test page sample aligned to the official case structure.

## Still required before a valid paid entry
- [ ] Run the official four practice cases (p00–p03) from the Make.fun kit and score the model; the repository's smoke fixture is synthetic and is not a substitute.
- [ ] Tune the forecast against practice scores and compare with the house baseline and house AI forecast.
- [ ] Restore GitHub Actions execution: GitHub reports that the account is locked due to a billing issue, so hosted jobs have not started.
- [ ] Create the required transcript bundle using the Make.fun kit CLI, with the genuine recorded agent session(s) and required run record. Do not fabricate or reconstruct transcripts.
- [ ] Sign the Make.fun entry message with the Solana wallet linked to the Make.fun account. The bounty escrow is on-chain.
- [ ] Submit the repository URL, full commit SHA, transcript bundle, signed entry message and signature through Make.fun before the deadline.

## Important
Make.fun's requirements say `handed_over_places: none`: a handed-over transcript may be ranked but is not eligible for a paid place. A valid reward-eligible entry therefore needs a recorded coding-agent session accepted by the kit's bundle checker. The current ChatGPT/GitHub work does not provide access to the user's private Make.fun wallet or a verifiable local harness session bundle, so no entry has been submitted or signed.
