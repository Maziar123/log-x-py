"""Export utilities for Eliot logs to various formats."""

from __future__ import annotations

import csv
import html
import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

from logxpy.parse import Task, WrittenAction


@dataclass
class ExportOptions:
    """Options for exporting logs."""

    indent: int | None = 2
    include_fields: list[str] | None = None
    exclude_fields: list[str] | None = None
    flatten: bool = False


def _extract_task_data(
    task: Task,
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
) -> dict[str, Any]:
    """Extract data from a task for export."""
    root = task.root()

    # Handle WrittenAction (parsed tasks) vs raw messages
    if isinstance(root, WrittenAction):
        data = {
            "task_uuid": root.task_uuid,
            "action_type": root.action_type,
        }

        # Get timestamp from start_message
        if root.start_message:
            data["timestamp"] = root.start_message.timestamp
            # Add all fields from start message contents
            for key, value in root.start_message.contents.items():
                if key not in data:
                    data[key] = value

        # Add end message data if available
        if root.end_message:
            data["action_status"] = root.end_message.contents.get("action_status", "unknown")
            data["end_time"] = root.end_message.timestamp
            if root.start_message:
                duration = root.end_message.timestamp - root.start_message.timestamp
                data["duration"] = round(duration, 6)
        else:
            data["action_status"] = "in_progress"
    else:
        # Fallback for other message types
        data = {
            "task_uuid": getattr(root, "task_uuid", "unknown"),
            "timestamp": getattr(root, "timestamp", None),
            "action_type": getattr(root, "action_type", "unknown"),
        }

    # Apply field filtering
    if include_fields:
        data = {k: v for k, v in data.items() if k in include_fields}
    if exclude_fields:
        data = {k: v for k, v in data.items() if k not in exclude_fields}

    return data


def export_json(
    tasks: Iterable[Any],
    output: TextIO | Path | str,
    options: ExportOptions | None = None,
    **kwargs: Any,
) -> int:
    """
    Export tasks to JSON format.

    Args:
        tasks: Tasks to export
        output: Output file path or file object
        options: Export options
        **kwargs: Ignored (for compatibility with export_tasks)

    Returns:
        Number of tasks exported

    Example:
        >>> export_json(tasks, "output.json")
        42
    """
    options = options or ExportOptions()
    count = 0

    def task_generator():
        nonlocal count
        for task in tasks:
            count += 1
            yield _extract_task_data(task, options.include_fields, options.exclude_fields)

    data = list(task_generator())

    # Handle output destination
    if isinstance(output, (str, Path)):
        with open(output, "w") as f:
            json.dump(data, f, indent=options.indent, default=str)
    else:
        json.dump(data, output, indent=options.indent, default=str)

    return count


def export_csv(
    tasks: Iterable[Any],
    output: TextIO | Path | str,
    options: ExportOptions | None = None,
    **kwargs: Any,
) -> int:
    """
    Export tasks to CSV format.

    Args:
        tasks: Tasks to export
        output: Output file path or file object
        options: Export options
        **kwargs: Ignored (for compatibility with export_tasks)

    Returns:
        Number of tasks exported

    Example:
        >>> export_csv(tasks, "output.csv")
        42
    """
    options = options or ExportOptions()
    data_list = []

    for task in tasks:
        data = _extract_task_data(task, options.include_fields, options.exclude_fields)
        data_list.append(data)

    if not data_list:
        return 0

    # Get fieldnames from first item
    fieldnames = list(data_list[0].keys())

    # Handle output destination
    if isinstance(output, (str, Path)):
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)
    else:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)

    return len(data_list)


def _generate_html(
    tasks: list[dict],
    title: str = "Eliot Log Export",
) -> str:
    """Generate HTML report from tasks."""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-color: #1e1e1e;
            --text-color: #d4d4d4;
            --header-bg: #2d2d2d;
            --border-color: #3e3e3e;
            --success-color: #4ec9b0;
            --error-color: #f48771;
            --warning-color: #dcdcaa;
            --info-color: #569cd6;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            color: var(--info-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }}
        .summary {{
            background-color: var(--header-bg);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: var(--header-bg);
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid var(--border-color);
            cursor: pointer;
        }}
        th:hover {{
            background-color: var(--border-color);
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
        }}
        tr:hover {{
            background-color: rgba(255, 255, 255, 0.05);
        }}
        .status-succeeded {{ color: var(--success-color); }}
        .status-failed {{ color: var(--error-color); }}
        .status-started {{ color: var(--warning-color); }}
        .json-field {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            background-color: rgba(0, 0, 0, 0.2);
            padding: 2px 5px;
            border-radius: 3px;
        }}
        .timestamp {{
            font-family: monospace;
            color: #858585;
        }}
        .duration {{
            text-align: right;
            font-family: monospace;
        }}
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            table {{ font-size: 0.9em; }}
            td, th {{ padding: 6px; }}
        }}
    </style>
</head>
<body>
    <h1>📊 {title}</h1>
    <div class="summary">
        <strong>Total Tasks:</strong> {count}<br>
        <strong>Generated:</strong> {generated_at}
    </div>
    <table id="logTable">
        <thead>
            <tr>
                {headers}
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    <script>
        // Simple table sorting
        document.querySelectorAll('th').forEach(header => {{
            header.addEventListener('click', () => {{
                const table = header.closest('table');
                const index = Array.from(header.parentNode.children).indexOf(header);
                const rows = Array.from(table.querySelectorAll('tbody tr'));
                const isAsc = header.classList.toggle('asc');
                
                rows.sort((a, b) => {{
                    const aVal = a.children[index].textContent;
                    const bVal = b.children[index].textContent;
                    return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                }});
                
                rows.forEach(row => table.querySelector('tbody').appendChild(row));
            }});
        }});
    </script>
</body>
</html>"""

    if not tasks:
        return html_template.format(
            title=html.escape(title),
            count=0,
            generated_at=datetime.now().isoformat(),
            headers="",
            rows="<tr><td>No tasks found</td></tr>",
        )

    # Generate headers
    headers = "".join(f"<th>{html.escape(str(k))}</th>" for k in tasks[0].keys())

    # Generate rows
    rows = []
    for task in tasks:
        cells = []
        for key, value in task.items():
            css_class = ""
            cell_content = html.escape(str(value))

            if key == "action_status":
                css_class = f"status-{value}" if value in ["succeeded", "failed", "started"] else ""
            elif key == "timestamp":
                css_class = "timestamp"
            elif key == "duration":
                css_class = "duration"
            elif isinstance(value, (dict, list)):
                cell_content = f'<span class="json-field">{html.escape(json.dumps(value, default=str))}</span>'

            cells.append(f'<td class="{css_class}">{cell_content}</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return html_template.format(
        title=html.escape(title),
        count=len(tasks),
        generated_at=datetime.now().isoformat(),
        headers=headers,
        rows="\n".join(rows),
    )


def export_html(
    tasks: Iterable[Any],
    output: TextIO | Path | str,
    options: ExportOptions | None = None,
    title: str = "Eliot Log Export",
) -> int:
    """
    Export tasks to HTML format with interactive table.
    
    Args:
        tasks: Tasks to export
        output: Output file path or file object
        options: Export options
        title: HTML page title
        
    Returns:
        Number of tasks exported
        
    Example:
        >>> export_html(tasks, "output.html", title="My Logs")
        42
    """
    options = options or ExportOptions()
    data_list = []

    for task in tasks:
        data = _extract_task_data(task, options.include_fields, options.exclude_fields)
        data_list.append(data)

    html_content = _generate_html(data_list, title)

    # Handle output destination
    if isinstance(output, (str, Path)):
        with open(output, "w") as f:
            f.write(html_content)
    else:
        output.write(html_content)

    return len(data_list)


def export_logfmt(
    tasks: Iterable[Any],
    output: TextIO | Path | str,
    options: ExportOptions | None = None,
    **kwargs: Any,
) -> int:
    """
    Export tasks to logfmt format (key=value pairs).

    Args:
        tasks: Tasks to export
        output: Output file path or file object
        options: Export options
        **kwargs: Ignored (for compatibility with export_tasks)

    Returns:
        Number of tasks exported

    Example:
        >>> export_logfmt(tasks, "output.log")
        42
    """
    options = options or ExportOptions()
    count = 0

    def format_value(v: Any) -> str:
        """Format a value for logfmt."""
        if isinstance(v, str):
            # Quote strings with spaces or special chars
            if " " in v or "=" in v or '"' in v:
                return f'"{v.replace("\"", "\\\"")}"'
            return v
        elif isinstance(v, (dict, list)):
            return json.dumps(v, default=str)
        return str(v)

    def format_task(data: dict) -> str:
        """Format a task as logfmt line."""
        pairs = []
        for key, value in data.items():
            formatted_value = format_value(value)
            pairs.append(f"{key}={formatted_value}")
        return " ".join(pairs)

    lines = []
    for task in tasks:
        count += 1
        data = _extract_task_data(task, options.include_fields, options.exclude_fields)
        lines.append(format_task(data))

    # Handle output destination
    if isinstance(output, (str, Path)):
        with open(output, "w") as f:
            f.write("\n".join(lines))
            if lines:
                f.write("\n")
    else:
        output.write("\n".join(lines))
        if lines:
            output.write("\n")

    return count


# Export formats registry
EXPORT_FORMATS: dict[str, Callable] = {
    "json": export_json,
    "csv": export_csv,
    "html": export_html,
    "logfmt": export_logfmt,
}


def export_tasks(
    tasks: Iterable[Any],
    output: TextIO | Path | str,
    format: str,
    options: ExportOptions | None = None,
    **kwargs: Any,
) -> int:
    """
    Export tasks to the specified format.
    
    Args:
        tasks: Tasks to export
        output: Output file path or file object
        format: Export format (json, csv, html, logfmt)
        options: Export options
        **kwargs: Additional format-specific arguments
        
    Returns:
        Number of tasks exported
        
    Example:
        >>> export_tasks(tasks, "out.json", "json")
        42
    """
    if format not in EXPORT_FORMATS:
        raise ValueError(f"Unknown format: {format}. Available: {list(EXPORT_FORMATS.keys())}")

    exporter = EXPORT_FORMATS[format]
    return exporter(tasks, output, options, **kwargs)


__all__ = [
    "EXPORT_FORMATS",
    "ExportOptions",
    "export_csv",
    "export_html",
    "export_json",
    "export_logfmt",
    "export_tasks",
]
