# Review log

Every check is made from the rendered MP4s (`python3 scripts/review.py <round>`) plus the per-beat contact sheets
(`node scripts/render.mjs --sheet`). Nothing is judged from the page. Critic prompt: the skill's `reference/CRITIQUE.md`.

Scores 1–10. Ship only when EVERY score is ≥ 8, after at least 3 rounds.

---

## Round 1: draft_16x9.mp4 (30 fps) + per-beat sheet, first full build

Critic run inline (no subagent in this session), evidence first.

| Criterion | Score | Evidence (timestamps, frames, metrics) |
|---|---|---|
| Hook (first 2 s) | 8 | f0 already shows "Give it" fully risen (stills t0/0.1/0.25, no mask slivers); "a topic." lands 0.5 s; real input card rises 0.75 s and types by 1.9 s. |
| Readability at phone size | 6 | phone_16x9 1 s: typed topic ≈ 5 px tall; 18–19 s: CTA "Try the live demo" ≈ 16 px and URL ≈ 7 px, smaller than the lockup, so the CTA is not the most legible thing (cap 6). Headlines all read. |
| Motion quality | 8 | strip_fast (10.4–10.8 s) shows a clean eased scroll, no jumps; headline swaps rise/lift through masks; indicator stretches between log lines (contact 4.5–9.5 s). No fades. |
| Variety / pacing | 8 | max_gap_between_visual_events 2.0 s (16 s), longest_static 1.0 s; 9 shots in 20 s; cuts on bar lines. |
| Brand accuracy | 9 | Every UI pixel is a real app.py capture; Source Sans, #FF4B4B single accent, #31333F ink. |
| Sound sync | 8 | -14.2 LUFS, TP -1.3 dBTP. Hits 13/21 within 45 ms, worst hits -67 ms (2 frames at 30 fps, picture early: spHit leads + cursor dip starts 60 ms early); no hit > 80 ms. |
| Composition | 6 | 14.0–14.5 s: memory window is two-thirds empty white main column with a tiny sidebar pill; 18–20 s end card leaves the right half and bottom third empty; 1.0–2.0 s input strip is a thin band in a large empty field. |
| Polish | 8 | no near_blank_frames; no double exposures at swaps (contact 2.0, 8.0, 15.0 s); caret hides after the click. Memory tooltip (real hover help text) partly covers "Past Sessions" at 15 s. |

**3 worst problems**
1. End card (18–20 s): CTA and URL are small (84 px / 38 px) and the frame is half empty, so the call to action is weaker than the lockup.
2. Memory (14.0–15.0 s): the window opens on an empty white main column; the saved-session pill is unreadable at phone size before the click.
3. Hook (0.75–2.0 s): input window at k 2.0 shows the typed topic at 28 px, ≈ 5 px on a phone; the band is thin against a large empty field.

**Fixes for round 2**
1. CTA 120 px, URL 48 px, lockup scale 2.7 → 3.1; verify phone frame at 19 s shows the CTA at least as tall as the caption line.
2. Memory camera starts tight on Past Sessions (k 3.2), the click pulls back to k 2 revealing the restored report; verify stills at 14.6 and 15.4 s.
3. Input window k 2.0 → 2.4, moved up to y 450 so the grown form still fits; cursor press dip starts 0.06 beat before the click instead of 0.12; verify stills at 1.6 and 3.3 s.

**Verdict:** ANOTHER ROUND

---

## Round 2: draft_16x9.mp4 after round-1 fixes

| Criterion | Score | Evidence (timestamps, frames, metrics) |
|---|---|---|
| Hook (first 2 s) | 8 | f0 "Give it" (stills t0–0.25 clean); input card at k 2.4 reads at 1 s in phone_16x9. |
| Readability at phone size | 7 | 19 s: CTA (124 px) now reads, but the lockup H1 (136 px) is still the biggest line, URL ≈ 9 px at 360 px. Typed topic ≈ 6 px (secondary). |
| Motion quality | 8 | strip_fast2 (15.0–15.37 s): memory window widens and pulls back on one spring, no jumps; swaps sequential. |
| Variety / pacing | 8 | max gap 2.0 s, longest static 1.0 s. |
| Brand accuracy | 9 | unchanged: real captures, one accent, Source Sans. |
| Sound sync | 7 | 12/21 within 45 ms; early -67 ms at 0.75 s (card), 2.5 s (click), 8.0 s (camera punch starts 150 ms before the click); late +67 ms at 15.0 s (pull-back starts after the click). |
| Composition | 7 | 12–14 s proof shot: right half empty; 14.0–15.0 s tight memory card fills the left half only (setup for the widen, acceptable for 1 s). |
| Polish | 8 | no blank frames, no double exposures; tooltip over "Past Sessions" is the app's real hover help. |

**3 worst problems**
1. Sound sync: card landing, Run click, gaps punch-in and session click read 2 frames off their sounds.
2. End card: CTA is not the most legible line; URL too small at phone size.
3. Proof shot (12–14 s): "74 s" + sub line leave the right half empty.

**Fixes for round 3**
1. Input card lands with a 3-frame lead (not half-travel); punch-in camera released 0.15 beat before the click (was 0.3); memory pull-back released 0.15 beat before the click (was +0.05 after). Verify with review.py sync.
2. Lockup scale 3.1 → 2.7, CTA 124 → 136 px, URL 48 → 54 px. Verify phone frame at 19 s: CTA is the largest line.
3. Proof shot: the real "Research complete / Agent log / Total run time" crop becomes a card on the right (k 2.4), rising one beat after the number. Verify still at 13.4 s.

**Verdict:** ANOTHER ROUND

---

## Round 3: draft_16x9.mp4 after round-2 fixes

| Criterion | Score | Evidence (timestamps, frames, metrics) |
|---|---|---|
| Hook (first 2 s) | 8 | f0 "Give it"; "a topic." 0.5 s; real input types 1.0–1.9 s. |
| Readability at phone size | 8 | phone_16x9 19 s: CTA (136 px) is the largest line, URL ≈ 10 px; every headline reads at 360 px; log text is supporting texture, the big agent words carry the beat. |
| Motion quality | 8 | strips: scroll and widen on springs, indicator stretch between rows, no pops; no fades. |
| Variety / pacing | 8 | max gap 2.0 s, longest static 1.0 s, 9 shots, cuts on bars, build → stop → drop into the lockup. |
| Brand accuracy | 9 | real captures only; #FF4B4B single accent; Source Sans. |
| Sound sync | 8 | 15/21 within 45 ms (was 12), mean 33 ms, none beyond ±67 ms (2 frames at 30 fps). Remaining early hits at 2.0 s / 9.0 s come from the outgoing headline lifting before the incoming lands (sequential-swap rule). 2.5 s: the hover state swaps in 125 ms before the click. |
| Composition | 8 | 12–14 s: number left, real completion card right, sub line under both; end card filled by lockup + CTA + URL. |
| Polish | 8 | no blank frames, no double exposures, caret gone after click. |

**3 worst problems**
1. 2.5 s: hover state swap 125 ms before the click reads as an early hit.
2. 13.0 s: "from topic to sourced report" reads 67 ms late (word stagger on a snappy rise).
3. Determinism not yet verified (`--verify`).

**Fixes for round 4**
1. Hover swap moves to b4.5 (cursor has arrived by then), outside the click window.
2. Sub line stagger 0.05 → 0.02 beats.
3. Run `render.mjs --verify`.

**Verdict:** ANOTHER ROUND (fixes are small; confirm in round 4)

---

## Round 4: draft after round-3 fixes

`render.mjs --verify`: 12/12 probes identical. Sync 16/21 within 45 ms (mean 31.7 ms). 2.5 s click still -67 ms: the form's grow spring and the cursor's arrival were still moving inside the click window. 13.0 s sub line now on time. All other scores as round 3.

**Fix for round 5:** form grows at b4.1 (was b4.5), cursor arrives from b3.8, so the press is the only motion near the click.

**Verdict:** ANOTHER ROUND

---

## Round 5: draft_16x9.mp4, final check before finals

| Criterion | Score | Evidence (timestamps, frames, metrics) |
|---|---|---|
| Hook (first 2 s) | 8 | f0 reads "Give it"; promise complete at 0.5 s; real input field typing by 1.0 s. |
| Readability at phone size | 8 | phone_16x9: every headline reads at 360 px; CTA is the largest line on the end card; URL ≈ 10 px (secondary, CTA carries it). |
| Motion quality | 8 | springs throughout (card rise, widen + pull-back, scroll, indicator stretch); no fades; no pops in strips. |
| Variety / pacing | 8 | new element at least every 2.0 s; 9 shots; build → stop-time → drop on the lockup. |
| Brand accuracy | 9 | real app.py captures only, measured palette, one accent, Source Sans. |
| Sound sync | 8 | 16/21 hits within 45 ms, mean 31.7 ms, worst ±67 ms (2 frames at 30 fps), none beyond 80 ms; -14.2 LUFS, TP -1.3 dBTP. Remaining early reads at 2.0 / 9.0 s are the outgoing headline lifting before the incoming lands (sequential-swap rule). |
| Composition | 8 | proof shot balanced (number, real completion card, sub line); memory card widens from the sidebar into the restored report; end card filled. |
| Polish | 8 | no blank frames, no double exposures, caret hidden after the click, determinism verified. |

**Known and accepted:** the Past Sessions tooltip at 15 s is the app's real hover help text; the log lines are a replay of the README's example run (disclosed in brief.md).

**Verdict:** SHIP

---
