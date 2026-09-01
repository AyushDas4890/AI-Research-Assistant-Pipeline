"""CLI entry point for the Ad QA pipeline.

Usage:
    python ad_qa_main.py path/to/ads.csv
    python ad_qa_main.py path/to/ads.csv --out-dir output

Input CSV columns (header row required): ad_id (optional), platform,
headline, body_copy, cta, destination_url, image_url. ``platform`` should be
one of the keys in ad_qa/config.py's PLATFORM_SPECS (currently
google_display, meta, linkedin) -- unrecognized platforms fall back to
google_display's spec.
"""

import argparse
import csv
import os
import sys
import uuid

from dotenv import load_dotenv

from ad_qa.graph_builder import build_ad_qa_graph
from utils.logger import get_logger

load_dotenv()
log = get_logger("ad_qa.main")


def load_ads_csv(path: str) -> list:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def initial_state(ads: list) -> dict:
    return {
        "ads": ads,
        "session_id": str(uuid.uuid4()),
        "ad_results": [],
        "report_md": "",
        "report_csv_rows": [],
        "agent_log": [],
        "error": None,
    }


def run_ad_qa(ads: list) -> dict:
    """Run the full ad QA graph over a list of ad-record dicts."""
    graph = build_ad_qa_graph()
    state = initial_state(ads)
    try:
        return graph.invoke(state)
    except Exception as exc:  # last-resort safety net
        log.error("Graph invocation failed: %s", exc)
        state["error"] = str(exc)
        state["report_md"] = f"# Ad QA Report\n\n_QA run failed: {exc}_"
        return state


def write_outputs(result: dict, out_dir: str) -> tuple:
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "ad_qa_report.md")
    csv_path = os.path.join(out_dir, "ad_qa_report.csv")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(result.get("report_md", "") or "(no report produced)")

    rows = result.get("report_csv_rows") or []
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ad_id", "platform", "status", "issue_count", "issues"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return md_path, csv_path


def main():
    parser = argparse.ArgumentParser(description="Run automated QA over a batch of ads.")
    parser.add_argument("ads_csv", help="Path to a CSV file of ad records.")
    parser.add_argument("--out-dir", default="output", help="Directory to write the report files to.")
    args = parser.parse_args()

    if not os.path.isfile(args.ads_csv):
        print(f"No such file: {args.ads_csv}")
        raise SystemExit(1)

    ads = load_ads_csv(args.ads_csv)
    if not ads:
        print("No ad rows found in the input CSV.")
        raise SystemExit(0)

    print(f"Running QA on {len(ads)} ad(s)...")
    result = run_ad_qa(ads)

    md_path, csv_path = write_outputs(result, args.out_dir)

    print("\n" + "=" * 60)
    print(result.get("report_md", "(no report produced)"))
    print("=" * 60)
    print(f"\nReport written to:\n  {md_path}\n  {csv_path}")

    if result.get("error"):
        print(f"\n[!] Completed with error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
