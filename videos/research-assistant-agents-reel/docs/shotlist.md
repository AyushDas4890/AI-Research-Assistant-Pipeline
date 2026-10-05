# Shotlist: AI Research Assistant reel · 20 s · 120 BPM · 40 beats · 16x9

STATUS: DRAFT — waiting for the user's OK. Nothing gets built until this says APPROVED.

Beats are on the measured grid (`beats.json`, 119.99 BPM, 0 ms residual). Every row lists what is NEW on screen. All UI is real (captured from `app.py`).

| # | Beats | Time (s) | Shot | On-screen text (exact) | Motion | SFX |
|---|---|---|---|---|---|---|
| 1 | 0–4 | 0.0–2.0 | **Hook.** Headline on `#F0F2F6`; the real "Research topic" input card rises under it and the topic types in | "Give it **a topic.**" · typed: "Future of AI coding agents and multimodal models" | "Give it" already up on frame 0, "a topic." rises b1 (heavy); input card rise b1.5 (default); typing b2–3.75 (real filled-field capture revealed left to right with caret) | pop b1, pop b1.5, ticks b2–3.75 |
| 2 | 4–8 | 2.0–4.0 | **Run.** Headline swaps; cursor presses the real red Run Research button; "Running agent pipeline…" status appears | "**Five** agents take it from here." | headline lift-out / rise-in b4; cursor glides to button, press b5 (snappy); UI swaps to running state b6; push 1.00→1.04 | pop b4, click b5, pop b6 |
| 3 | 8–16 | 4.0–8.0 | **The run.** Hard cut. Left: one big word per agent. Right: the real log card; each new log line lands with an accent bar beside it | "Plan." → "Search." → "Read." → "Critique." | word swaps b8/10/12/14 (heavy, sequential); log card swaps to each real step capture; indicator bar steps down line by line (snappy lead) | pop b8, b10, b12, b14 |
| 4 | 16–20 | 8.0–10.0 | **Self-critique.** Camera punches in on the Critic line; accent underline snaps under `gaps_found: True`; then the retry line `[SEARCHER] … retry: 1` lands | "Finds its own **gaps.**" → "Searches again." | punch-in b16 (default); underline b16 (snappy); headline swap + new line b18 | click b16, whoosh + pop b18 |
| 5 | 20–24 | 10.0–12.0 | **Report.** Hard cut to the real finished page: "✅ Research complete", then it scrolls to the report title and Executive Summary | "Writes a sourced report." | scroll b20–22 (seg + ease), accent highlight on the H1 b22; push | whoosh b20, pop b22 |
| 6 | 24–28 | 12.0–14.0 | **Proof.** Big counter rolls up to the real run time; the real "⏱️ Total run time: 74.1s" crop sits under it | "**74 s**" · "from topic to sourced report" | counter 0→74 over b24–25.5; sub line rises b26 | pop b24, ticks b24.25–25.25, pop b26 |
| 7 | 28–32 | 14.0–16.0 | **Memory.** Hard cut to the real sidebar after a reload: the run now sits in "Past Sessions"; cursor clicks it and the report comes back | "Saved to **memory.**" → "The next run starts smarter." | session pill rises b28 (snappy); cursor click b30, page swaps to loaded state; headline swap b30 | pop b28, click b30 |
| 8 | 32–36 | 16.0–18.0 | **Architecture.** The real "Agent Graph" sidebar card; an accent bar walks Planner → Searcher → Reader → Critic → back to Searcher → … → Writer | "One LangGraph graph. Five agents." | indicator steps every half beat b32.5–35 (stretch on move); push | pop b32, ticks b32.5–34.5, music builds then stops at b35.5 |
| 9 | 36–40 | 18.0–20.0 | **End card.** The app's real H1 lockup "🔬 AI Research Assistant" + its caption; CTA + URL underneath. Never static: slow push + underline sweep through the CTA | "Try the **live demo**" · "ayushdas4890-ai-research-assistant-pipeline-app-1sjuvf.streamlit.app" | lockup rises b36 (heavy), CTA b37, URL b37.5 (snappy); push 1.00→1.06; sweep b38.5 | riser → thump b36, pop b37, pop b37.5 |

Rule check: something new at least every 2 s (every bar has 2+ events) · hook reads on frame 0 ("Give it") and fully by 0.6 s · end card holds 2 s with continuous push + sweep · hard cuts only on bar lines.

## Music
Synth, Am–F–C–G, one chord per bar. Intro b0 → full groove b8 (first agent) → build b32 (graph) → stop-time gap b35.5 → drop + crash on the lockup b36.

## Honesty notes
- The run is a replay: `capture_app/` swaps the LLM graph and ChromaDB for stubs emitting the same node updates, so the real `app.py` renders real UI without API keys. Log lines follow the README's observability example (the second critic pass `Coverage: 0.94` is filled in by the replay); report text is from `docs/report.png`; the 74 s run time matches the live screenshot (74.2 s).

## Open questions for the user
- None blocking. Duration is set to 20 s (you picked 16:9 without a length).
