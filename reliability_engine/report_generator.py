"""
Report Generator for BREL Reliability Engine.
Transforms raw execution and metrics data into publication-ready Markdown reports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ReportGenerator:
    """Generates structured Markdown reports from repeatability run manifests."""

    @staticmethod
    def generate_markdown_report(manifest: Dict[str, Any], output_path: Path) -> Path:
        metrics = manifest.get("metrics", {})
        analysis = manifest.get("analysis", {})
        lat = metrics.get("latency", {})
        ci = metrics.get("pass_rate_ci_95", {})

        md = f"""# Reliability Engineering Laboratory: Experiment Report

**Run ID:** `{manifest.get('run_id')}`  
**Test Target:** `{manifest.get('test_target')}`  
**Browser Engine:** `{manifest.get('browser')}` (Headless)  
**Sample Size:** $N = {manifest.get('iterations')}$ iterations  
**Timestamp (UTC):** `{manifest.get('timestamp_utc')}`  

---

## 1. Executive Summary & Verdict

| Metric | Measured Value | Standard / Description |
|---|---|---|
| **Verdict** | **`{analysis.get('verdict')}`** | Overall stability classification |
| **Is Flaky?** | **`{'YES' if analysis.get('is_flaky') else 'NO'}`** | Intermittent or retry-passed instability |
| **First-Attempt Pass Rate (FPR)** | **{metrics.get('first_attempt_pass_rate_pct')}%** | Passes on first attempt without retries |
| **Failure Rate (FR)** | **{metrics.get('failure_rate_pct')}%** | First attempt failures |
| **95% Confidence Interval** | **[{ci.get('lower')}%, {ci.get('upper')}%]** | Wilson score interval for true pass rate |
| **Rule of Three Upper Bound** | **{metrics.get('rule_of_three_upper_bound_pct', 'N/A')}%** | Maximum failure risk under 0 observed failures |

> **Statistical Note:** {metrics.get('statistical_disclaimer')}

---

## 2. Execution Latency Profile

| Percentile | Latency (ms) |
|---|---|
| **Min** | {lat.get('min_ms')} ms |
| **Median ($P_{{50}}$)** | {lat.get('median_ms')} ms |
| **90th Percentile ($P_{{90}}$)** | {lat.get('p90_ms')} ms |
| **95th Percentile ($P_{{95}}$)** | {lat.get('p95_ms')} ms |
| **Max** | {lat.get('max_ms')} ms |
| **Mean** | {lat.get('mean_ms')} ms |

---

## 3. Failure Classification Distribution

"""
        failure_dist = analysis.get("failure_distribution", {})
        if not failure_dist:
            md += "Zero failures observed during this repeatability experiment.\n"
        else:
            md += "| Category | Count | Percentage |\n|---|---|---|\n"
            total_fails = sum(failure_dist.values())
            for cat, count in failure_dist.items():
                pct = round(count / total_fails * 100, 1)
                md += f"| **{cat}** | {count} | {pct}% |\n"

        md += """
---

## 4. Iteration Log Preview

| Iteration | Outcome | Duration (ms) | Failure Category |
|---|---|---|---|
"""
        iterations_data = manifest.get("iterations_data", [])
        for r in iterations_data[:15]:
            outcome = "PASS" if r.get("passed") else "FAIL"
            md += f"| #{r.get('iteration')} | **{outcome}** | {r.get('duration_ms')} ms | {r.get('failure_category') or 'None'} |\n"

        if len(iterations_data) > 15:
            md += f"| ... | ... | ... | *({len(iterations_data) - 15} additional iterations omitted)* |\n"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)

        return output_path
