"""
Export functionality for logxy-log-parser.

Contains exporters for various formats: JSON, CSV, HTML, Markdown, and DataFrame.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .filter import LogEntries


class JsonExporter:
    """Export log entries to JSON format."""

    def export(self, entries: LogEntries, file: str | Path, pretty: bool = True) -> None:
        """Export entries to JSON file.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
            pretty: Pretty-print JSON if True.
        """
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = [entry.to_dict() for entry in entries]

        with open(path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)


class CsvExporter:
    """Export log entries to CSV format."""

    def export(self, entries: LogEntries, file: str | Path, flatten: bool = True) -> None:
        """Export entries to CSV file.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
            flatten: Flatten nested fields if True.
        """
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not entries:
            # Create empty file with headers
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([])
            return

        # Collect all field names
        fieldnames: set[str] = set()
        rows: list[dict[str, Any]] = []

        for entry in entries:
            row: dict[str, Any] = {
                "timestamp": entry.timestamp,
                "task_uuid": entry.task_uuid,
                "level": entry.level.value,
                "message_type": entry.message_type,
                "message": entry.message or "",
                "action_type": entry.action_type or "",
                "action_status": entry.action_status.value if entry.action_status else "",
                "duration": entry.duration or "",
            }

            if flatten:
                # Flatten nested fields
                for key, value in entry.fields.items():
                    if isinstance(value, (dict, list)):
                        # Convert complex types to JSON string
                        row[f"field_{key}"] = json.dumps(value)
                    else:
                        row[f"field_{key}"] = value
            else:
                # Add fields as JSON string
                if entry.fields:
                    row["fields"] = json.dumps(entry.fields)

            fieldnames.update(row.keys())
            rows.append(row)

        # Write CSV
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer: csv.DictWriter[str] = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(rows)


class HtmlExporter:
    """Export log entries to HTML format."""

    _DEFAULT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Entries</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ margin-top: 0; color: #333; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }}
        .stat {{ background: #f0f0f0; padding: 10px 15px; border-radius: 4px; }}
        .stat-label {{ font-weight: bold; color: #666; }}
        .stat-value {{ font-size: 1.2em; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
        tr:hover {{ background: #f5f5f5; }}
        .level-debug {{ color: #6c757d; }}
        .level-info {{ color: #0d6efd; }}
        .level-success {{ color: #198754; }}
        .level-warning {{ color: #fd7e14; }}
        .level-error {{ color: #dc3545; }}
        .level-critical {{ color: #6f42c1; font-weight: bold; }}
        .timestamp {{ font-family: monospace; color: #666; }}
        .message {{ max-width: 500px; overflow-wrap: break-word; }}
        .fields {{ font-size: 0.9em; color: #666; }}
        .fields pre {{ margin: 0; white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Log Entries</h1>
        <div class="stats">
            <div class="stat"><span class="stat-label">Total:</span> <span class="stat-value">{count}</span></div>
            <div class="stat"><span class="stat-label">Errors:</span> <span class="stat-value">{errors}</span></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Level</th>
                    <th>Message</th>
                    <th>Action</th>
                    <th>Duration</th>
                    <th>Fields</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    def export(self, entries: LogEntries, file: str | Path, template: str | None = None) -> None:
        """Export entries to HTML file.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
            template: Optional HTML template path. Uses default if None.
        """
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Load template
        if template:
            with open(template, encoding="utf-8") as f:
                html_template = f.read()
        else:
            html_template = self._DEFAULT_TEMPLATE

        # Build rows
        rows = []
        error_count = 0

        for entry in entries:
            if entry.is_error:
                error_count += 1

            # Format timestamp
            from .utils import format_timestamp
            ts_str = format_timestamp(entry.timestamp)

            # Format duration
            duration_str = ""
            if entry.duration is not None:
                from .utils import parse_duration
                duration_str = parse_duration(entry.duration)

            # Format fields
            fields_str = ""
            if entry.fields:
                fields_str = f'<div class="fields"><pre>{json.dumps(entry.fields, indent=2)}</pre></div>'

            row = f"""
                <tr>
                    <td class="timestamp">{ts_str}</td>
                    <td class="level-{entry.level.value}">{entry.level.value.upper()}</td>
                    <td class="message">{entry.message or '-'}</td>
                    <td>{entry.action_type or '-'}</td>
                    <td>{duration_str}</td>
                    <td>{fields_str}</td>
                </tr>
            """
            rows.append(row)

        # Fill template
        html = html_template.format(
            count=len(entries),
            errors=error_count,
            rows="".join(rows),
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def export_report(self, _analysis: Any, file: str | Path) -> None:
        """Export analysis report to HTML file.

        Args:
            analysis: LogAnalysis object to export.
            file: Output file path.
        """
        # Placeholder for analysis report export
        # Will be implemented when analyzer module is complete
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Log Analysis Report</title>
</head>
<body>
    <h1>Log Analysis Report</h1>
    <p>Analysis report export not yet implemented.</p>
</body>
</html>
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)


class MarkdownExporter:
    """Export log entries to Markdown format."""

    def export(self, entries: LogEntries, file: str | Path) -> None:
        """Export entries to Markdown file.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
        """
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        from .utils import format_timestamp, parse_duration

        lines = [
            "# Log Entries\n",
            f"**Total Entries:** {len(entries)}\n",
            "",
            "| Timestamp | Level | Message | Action | Duration |",
            "|-----------|-------|---------|--------|----------|",
        ]

        for entry in entries:
            ts_str = format_timestamp(entry.timestamp)
            level_str = entry.level.value.upper()
            message_str = (entry.message or "-").replace("|", "\\|")
            action_str = entry.action_type or "-"
            duration_str = parse_duration(entry.duration) if entry.duration else "-"

            lines.append(f"| {ts_str} | {level_str} | {message_str} | {action_str} | {duration_str} |")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def export_table(self, entries: LogEntries, file: str | Path) -> None:
        """Export entries to Markdown table file.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
        """
        self.export(entries, file)


class DataFrameExporter:
    """Export log entries to pandas DataFrame."""

    def export(self, entries: LogEntries) -> Any:
        """Export entries to pandas DataFrame.

        Args:
            entries: LogEntries collection to export.

        Returns:
            pd.DataFrame: DataFrame containing log entries.

        Raises:
            ImportError: If pandas is not installed.
        """
        try:
            import pandas  # type: ignore
        except ImportError as e:
            raise ImportError(
                "pandas is required for DataFrame export. "
                "Install with: pip install logxy-log-parser[pandas]"
            ) from e

        # Convert entries to list of dicts
        data = []
        for entry in entries:
            row = {
                "timestamp": entry.timestamp,
                "task_uuid": entry.task_uuid,
                "level": entry.level.value,
                "message_type": entry.message_type,
                "message": entry.message,
                "action_type": entry.action_type,
                "action_status": entry.action_status.value if entry.action_status else None,
                "duration": entry.duration,
            }
            # Add fields as columns
            row.update(entry.fields)
            data.append(row)

        return pandas.DataFrame(data)


class PdfExporter:
    """Export log entries to PDF format."""

    def __init__(self) -> None:
        """Initialize PDF exporter."""
        self._weasyprint_available = self._check_weasyprint()

    def _check_weasyprint(self) -> bool:
        """Check if WeasyPrint is available.

        Returns:
            bool: True if WeasyPrint is available.
        """
        try:
            import weasyprint  # type: ignore  # noqa: F401
            return True
        except ImportError:
            return False

    def export(self, entries: LogEntries, file: str | Path, template: str | None = None) -> None:
        """Export entries to PDF file.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
            template: Optional HTML template path.

        Raises:
            ImportError: If WeasyPrint is not installed.
        """
        if not self._weasyprint_available:
            raise ImportError(
                "WeasyPrint is required for PDF export. "
                "Install with: pip install logxy-log-parser[pdf]"
            )

        import weasyprint  # type: ignore

        # First generate HTML
        html_exporter = HtmlExporter()
        html_path = Path(file).with_suffix(".html.tmp")

        try:
            html_exporter.export(entries, html_path, template=template)

            # Convert HTML to PDF
            weasyprint.HTML(filename=str(html_path)).write_pdf(str(file))

        finally:
            # Clean up temp HTML file
            if html_path.exists():
                html_path.unlink()


class CustomTemplateExporter:
    """Export log entries using custom templates."""

    def export(
        self,
        entries: LogEntries,
        file: str | Path,
        template_path: str | Path,
        template_format: str = "html",
    ) -> None:
        """Export entries using a custom template.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
            template_path: Path to template file.
            template_format: Template format (html, md, txt).

        Raises:
            ValueError: If template format is not supported.
        """
        template_path = Path(template_path)
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Read template
        with open(template_path, encoding="utf-8") as f:
            template_content = f.read()

        # Collect template variables
        from .utils import format_timestamp, parse_duration

        # Build entry data
        entries_data = []
        for entry in entries:
            entries_data.append({
                "timestamp": entry.timestamp,
                "timestamp_str": format_timestamp(entry.timestamp),
                "task_uuid": entry.task_uuid,
                "level": entry.level.value,
                "message": entry.message or "",
                "action_type": entry.action_type or "",
                "action_status": entry.action_status.value if entry.action_status else "",
                "duration": entry.duration,
                "duration_str": parse_duration(entry.duration) if entry.duration else "",
                "fields": entry.fields,
            })

        # Calculate stats
        level_counts: dict[str, int] = {}
        error_count = 0
        for entry in entries:
            level_counts[entry.level.value] = level_counts.get(entry.level.value, 0) + 1
            if entry.is_error:
                error_count += 1

        # Template variables
        context = {
            "entries": entries_data,
            "count": len(entries),
            "errors": error_count,
            "level_counts": level_counts,
        }

        # Simple template substitution (for advanced templating, use Jinja2)
        output = template_content
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            output = output.replace(placeholder, str(value))

        # Write output
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)


class Jinja2Exporter:
    """Export log entries using Jinja2 templates."""

    def __init__(self) -> None:
        """Initialize Jinja2 exporter."""
        self._jinja2_available = self._check_jinja2()

    def _check_jinja2(self) -> bool:
        """Check if Jinja2 is available.

        Returns:
            bool: True if Jinja2 is available.
        """
        try:
            import jinja2  # type: ignore  # noqa: F401
            return True
        except ImportError:
            return False

    def export(
        self,
        entries: LogEntries,
        file: str | Path,
        template_path: str | Path,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Export entries using Jinja2 template.

        Args:
            entries: LogEntries collection to export.
            file: Output file path.
            template_path: Path to Jinja2 template file.
            context: Additional template context variables.

        Raises:
            ImportError: If Jinja2 is not installed.
        """
        if not self._jinja2_available:
            raise ImportError(
                "Jinja2 is required for custom template export. "
                "Install with: pip install logxy-log-parser[templates]"
            )

        import jinja2  # type: ignore

        template_path = Path(template_path)
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path.parent),
            autoescape=jinja2.select_autoescape(),
        )

        template = env.get_template(template_path.name)

        # Build context
        from .utils import format_timestamp, parse_duration

        entries_data = []
        level_counts: dict[str, int] = {}
        error_count = 0

        for entry in entries:
            level_counts[entry.level.value] = level_counts.get(entry.level.value, 0) + 1
            if entry.is_error:
                error_count += 1

            entries_data.append({
                "timestamp": entry.timestamp,
                "timestamp_str": format_timestamp(entry.timestamp),
                "task_uuid": entry.task_uuid,
                "level": entry.level.value,
                "message": entry.message or "",
                "action_type": entry.action_type or "",
                "action_status": entry.action_status.value if entry.action_status else "",
                "duration": entry.duration,
                "duration_str": parse_duration(entry.duration) if entry.duration else "",
                "fields": entry.fields,
                "entry": entry,  # Full entry access
            })

        template_context = {
            "entries": entries_data,
            "count": len(entries),
            "errors": error_count,
            "level_counts": level_counts,
        }

        if context:
            template_context.update(context)

        # Render and write
        output = template.render(**template_context)

        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
