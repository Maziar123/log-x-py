#!/usr/bin/env python3
"""
13_export_data.py - Export Feature

Demonstrates export functionality:
- JSON, CSV, HTML, Markdown export
- DataFrame export (with pandas)
"""
from __future__ import annotations

import tempfile
from pathlib import Path

# Create sample log first
from logxpy import log, to_file, start_action


def create_sample_log() -> Path:
    """Create a sample log file for export demonstration."""
    log_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
    log_path = Path(log_file.name)

    if log_path.exists():
        log_path.unlink()
    with open(log_path, "w", encoding="utf-8") as f:
        to_file(f)

    # Generate diverse log entries
    with start_action("user:login", user_id=123):
        log.info("User authenticated", username="alice")
        log.success("Login successful")

    with start_action("database:query", table="users"):
        log.info("Executing query", sql="SELECT * FROM users")
        log.success("Query completed", rows=42)

    log.warning("High memory usage", memory_percent=85)
    log.error("API timeout", endpoint="/api/users", timeout_ms=5000)

    with start_action("data:export", format="csv"):
        log.info("Exporting data", records=1000)
        log.success("Export completed", file="export.csv")

    return log_path


def main():
    """Demonstrate export functionality."""
    from logxy_log_parser import parse_log
    from logxy_log_parser.filter import LogEntries

    # Create sample log
    log_path = create_sample_log()
    print(f"Created sample log: {log_path}")

    # Create output directory
    output_dir = Path(tempfile.gettempdir()) / "logxy_export_examples"
    output_dir.mkdir(exist_ok=True)

    # Parse entries
    entries = parse_log(log_path)
    log_entries = LogEntries(entries)

    # ========================================
    # 1. JSON EXPORT
    # ========================================
    print("\n" + "=" * 60)
    print("1. JSON EXPORT - Structured Data Format")
    print("=" * 60)

    json_path = output_dir / "export.json"
    log_entries.to_json(json_path, pretty=True)
    print(f"Exported to JSON: {json_path}")
    print(f"  File size: {json_path.stat().st_size} bytes")

    # ========================================
    # 2. CSV EXPORT
    # ========================================
    print("\n" + "=" * 60)
    print("2. CSV EXPORT - Spreadsheet Compatible")
    print("=" * 60)

    csv_path = output_dir / "export.csv"
    log_entries.to_csv(csv_path, flatten=True)
    print(f"Exported to CSV: {csv_path}")
    print(f"  File size: {csv_path.stat().st_size} bytes")

    # Show first few lines
    with open(csv_path, encoding="utf-8") as f:
        lines = f.readlines()[:3]
        print(f"  Preview: {lines[0].strip()}")
        print(f"           {lines[1].strip() if len(lines) > 1 else ''}")

    # ========================================
    # 3. HTML EXPORT
    # ========================================
    print("\n" + "=" * 60)
    print("3. HTML EXPORT - Browser Viewable Report")
    print("=" * 60)

    html_path = output_dir / "export.html"
    log_entries.to_html(html_path)
    print(f"Exported to HTML: {html_path}")
    print(f"  File size: {html_path.stat().st_size} bytes")
    print(f"  View in browser: file://{html_path}")

    # ========================================
    # 4. MARKDOWN EXPORT
    # ========================================
    print("\n" + "=" * 60)
    print("4. MARKDOWN EXPORT - Documentation Format")
    print("=" * 60)

    md_path = output_dir / "export.md"
    log_entries.to_markdown(md_path)
    print(f"Exported to Markdown: {md_path}")
    print(f"  File size: {md_path.stat().st_size} bytes")

    # Show first few lines
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()[:3]
        for line in lines:
            print(f"  {line.rstrip()}")

    # ========================================
    # 5. DATAFRAME EXPORT (with pandas)
    # ========================================
    print("\n" + "=" * 60)
    print("5. DATAFRAME EXPORT - Pandas Integration")
    print("=" * 60)

    try:
        df = log_entries.to_dataframe()
        print(f"Created DataFrame: {len(df)} rows x {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns)[:5]}...")
        print(f"  Shape: {df.shape}")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        # Export DataFrame to CSV
        df_csv_path = output_dir / "export_dataframe.csv"
        df.to_csv(df_csv_path, index=False)
        print(f"  DataFrame CSV: {df_csv_path}")

    except ImportError:
        print("  pandas not installed - skipping DataFrame export")
        print("  Install with: pip install logxy-log-parser[pandas]")

    # ========================================
    # 6. PDF EXPORT (with weasyprint)
    # ========================================
    print("\n" + "=" * 60)
    print("6. PDF EXPORT - Professional Reports")
    print("=" * 60)

    try:
        from logxy_log_parser.export import PdfExporter
        pdf_exporter = PdfExporter()
        pdf_path = output_dir / "export.pdf"
        pdf_exporter.export(log_entries, pdf_path)
        print(f"Exported to PDF: {pdf_path}")
        print(f"  File size: {pdf_path.stat().st_size} bytes")

    except ImportError:
        print("  WeasyPrint not installed - skipping PDF export")
        print("  Install with: pip install logxy-log-parser[pdf]")

    # Cleanup
    log_path.unlink()

    print(f"\n" + "=" * 60)
    print(f"Export examples complete! Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
