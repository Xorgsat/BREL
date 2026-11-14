#!/usr/bin/env python3
"""
CLI Utility to run and generate Cross-Framework Comparative Reports.
Contrasts Selenium WebDriver vs Playwright Test across empirical reliability experiments.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

# Ensure root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reliability_engine.comparison_engine import ComparisonEngine


def main():
    print("=" * 60)
    print("  BREL CROSS-FRAMEWORK COMPARATIVE ANALYSIS ENGINE")
    print("=" * 60)
    print("Executing empirical comparison between Selenium WebDriver and Playwright Test...\n")

    engine = ComparisonEngine(reports_dir=Path("reports"))
    report = engine.generate_comparison_matrix()

    json_path = Path("reports/framework_comparison.json")
    md_path = Path("reports/framework_comparison.md")

    # Write JSON
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    # Write Markdown
    markdown_content = engine.render_markdown(report)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print("\n" + "=" * 60)
    print(f"Comparison Analysis Complete!")
    print(f"Total Scenarios Compared: {report.total_scenarios_compared}")
    print(f"Selenium Aggregate Time:  {report.selenium_total_duration_ms} ms")
    print(f"Playwright Aggregate Time: {report.playwright_total_duration_ms} ms")
    print(f"Speedup Ratio:             {report.aggregate_speedup_ratio}x")
    print(f"JSON Artifact:             {json_path}")
    print(f"Markdown Report:           {md_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
