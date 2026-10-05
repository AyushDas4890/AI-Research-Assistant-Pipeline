# Style guide: AI Research Assistant reel

Source material: `assets/site/info.json`, `assets/cap/*.png` (real UI of `app.py`, 3200x2000 @2x), `../../docs/*.png` (live-site screenshots from the README). No reference film: grammar comes from the house rules.

## 1. Palette (measured, not guessed)
| Token | Hex | Source |
|---|---|---|
| `--bg` | `#F0F2F6` | Streamlit sidebar / input fill (measured pixel) |
| `--card` | `#FFFFFF` | app canvas |
| `--code` | `#F8F9FB` | `st.code` block background (measured pixel) |
| `--ink` | `#31333F` | headline + body text (`rgb(49, 51, 63)`) |
| `--ink-2` | `#808495` | caption text (`rgba(49, 51, 63, 0.6)` on white) |
| `--accent` | `#FF4B4B` | primary "Run Research" button + focus ring: the ONE accent |

## 2. Type
- Display face: **Source Sans** 700 (`assets/fonts/source-sans-100_900.woff2`, variable). The app's H1 uses it at 700. Tracking -0.02em, line-height 0.95, sentence case, full stops on statements (the app's labels don't use them, but the film's claims are short sentences).
- UI face: Source Sans 400/600, same file. Source Code Pro appears only inside the real UI captures (the agent log), never as film type.
- Sizes at 1080p: hero 150–190 px, secondary 64–90 px, nothing that must be read below 36 px. UI crops are scaled by the camera so log text is ≥ 28 px on screen.
- Accent on the key word only: "topic.", "Five", "gaps.", "74 s", "memory.", "live demo".

## 3. Rhythm
120 BPM, 2 s bars, 20 s = 10 bars. Hard cuts on bar lines (b8, b20, b24, b28, b32, b36). Inner events on beats: one log line per 2 beats during the run. Nothing holds longer than one bar without a new element.

## 4. Transitions (allowed vocabulary)
Hard cut on the bar · card rise (UI card springs up from below) · camera punch-in on a UI line · scroll inside the real page · headline swap (lift out through the mask, next rises in).
Never: crossfades, spins, glitches, light leaks.

## 5. Camera
Every hold has a micro push of 1.00 → 1.04. Punch-ins on UI use the `default` spring. No CSS 3D. Depth comes from a soft, wide shadow under the UI cards on the `--bg` canvas.

## 6. Texture & finish
Clean digital, flat light. White UI cards with 18 px radius and deep soft shadow on `#F0F2F6`. No grain, no glow.

## 7. Text in / out
Enter: rise through a mask (`heavy` for headlines, `snappy` for small lines). Exit: lift through the mask, or a hard cut. UI highlight = accent bar / underline driven by `Motion.indicator`. Cursor = small dark arrow, moves on `default`, press = scale 0.9 on `snappy`.

## 8. Sound
Synth score at 120 BPM: intro (b0), full groove from the first agent (b8), build under the agent graph (b32), stop-time gap at b35.5, drop on the end card (b36). SFX: pops for each headline / log line, ticks for typing and the counter, clicks for cursor presses, whoosh into the report, riser + thump on the lockup. No voiceover.
