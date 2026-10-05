# Brief

| Input | Value |
|---|---|
| Product | AI Research Assistant: a 5-agent LangGraph pipeline (Planner, Searcher, Reader, Critic, Writer) with a self-critique retry loop and ChromaDB long-term memory |
| URL | https://ayushdas4890-ai-research-assistant-pipeline-app-1sjuvf.streamlit.app/ (blocked by this session's egress policy; real UI captured from the same `app.py` run locally, see `capture_app/`) |
| One-line promise | Give it a topic. Five agents research it, check their own work, and write a sourced report. |
| Audience / platform | Portfolio / recruiters: README, LinkedIn, GitHub. Must read with sound off. |
| Duration (s) | 20 |
| Formats | 16x9 only |
| Brand colours | Streamlit app theme, measured: ink `#31333F`, canvas `#FFFFFF`, sidebar `#F0F2F6`, accent `#FF4B4B` (primary button / focus ring) |
| Fonts | Source Sans (display + UI), Source Code Pro (log / numbers). Both served by the app itself, in `assets/fonts/` |
| Reference film | none: rhythm from the house rules |
| Music | `synth` (scripts/music.py), 120 BPM |
| Voiceover | none (no Fish Audio connector in this session) |
| CTA / end card | "Try the live demo" + streamlit.app URL |
| Must show | typing a topic + Run; the five agents working (live log); Critic finding gaps and re-searching; the finished report; memory (past session); the agent graph |
| Must avoid | redrawn UI, invented features |

## Messages, in order
1. Give it a topic.
2. Five agents take it from there: plan, search, read, critique.
3. The Critic finds its own gaps and searches again.
4. A sourced report, saved to memory.
5. Built as one LangGraph graph. Try the live demo.

## Notes
- All product UI is real: screenshots of the unmodified `app.py` (Streamlit 1.65) driven by Playwright. `capture_app/` swaps the LLM graph and ChromaDB for a replay that emits the same node updates, so no API keys are needed. Log lines follow the README's observability example; the report text is from `docs/report.png`; replay timing gives the 74 s run time shown in that screenshot.
