# Ad QA Automation

A batch QA pipeline for ad creatives, built on the same LangGraph
architecture as the research assistant in this repo (typed state, one node
per concern, everything logged to `agent_log`).

## What it checks

| Agent | Check | Depends on LLM? |
|---|---|---|
| `link_checker` | Destination URL loads, redirect count, latency | No |
| `image_qa` | Format, file size, dimensions vs. platform spec | No |
| `copy_compliance` | Banned/risky terms, character limits, then LLM review for unsubstantiated claims and missing disclaimers | Deterministic pass: no. LLM pass: yes |
| `policy_compliance` | LLM review against Google/Meta/LinkedIn-style ad policy risk categories | Yes |
| `reporter` | Aggregates into a Markdown report + CSV rows, worst-first | No |

Each ad ends up `PASS`, `WARN`, or `FAIL` (FAIL if any check found a FAIL-level
issue, WARN if only warnings, PASS otherwise).

## Running it

```bash
python ad_qa_main.py sample_ads.csv
```

Writes `output/ad_qa_report.md` and `output/ad_qa_report.csv`. Needs
`OPENAI_API_KEY` set (same `.env` as the research pipeline) for the copy and
policy checks -- the link and image checks work without it.

## Input format

CSV with columns: `ad_id` (optional, auto-generated if blank), `platform`
(`google_display` / `meta` / `linkedin` -- unrecognized values fall back to
`google_display`'s spec), `headline`, `body_copy`, `cta`, `destination_url`,
`image_url`.

## Customizing for your brand

`ad_qa/config.py` holds everything that should be tuned before this is
trusted for real ad submissions:

- `PLATFORM_SPECS` -- image size/format/file-size rules per platform.
- `COPY_LIMITS` -- headline/body character limits per platform.
- `BANNED_OR_RISKY_TERMS` -- deterministic red-flag word list.
- `DISCLAIMER_TRIGGER_KEYWORDS` -- claim categories that usually need a
  disclosure.

These are reasonable starting points, not verified against current platform
policy pages -- cross-check before relying on them for real launches.

## Extending it

To add a new check, follow the pattern in any `ad_qa/agents/*.py` file: read
`state["ad_results"]`, mutate each ad's `checks` and `issues`, return the
updated list plus a log line. Then register it as a node in
`ad_qa/graph_builder.py`.
