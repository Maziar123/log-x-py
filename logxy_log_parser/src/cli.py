"""
Command Line Interface for logxy-log-parser.

Provides CLI tools for querying, analyzing, and viewing LogXPy log files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    click = None  # type: ignore


# Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


def style(text: str, fg: str | None = None, bold: bool = False) -> str:
    """Apply terminal styling to text.

    Args:
        text: Text to style.
        fg: Foreground color name.
        bold: Make text bold.

    Returns:
        str: Styled text (or original if colors disabled).
    """
    # Check if NO_COLOR environment variable is set
    if "NO_COLOR" in dict(__import__("os").environ):
        return text

    # Check if we're in a non-TTY environment
    if not sys.stdout.isatty():
        return text

    color_map = {
        "red": Colors.RED,
        "green": Colors.GREEN,
        "yellow": Colors.YELLOW,
        "blue": Colors.BLUE,
        "magenta": Colors.MAGENTA,
        "cyan": Colors.CYAN,
        "white": Colors.WHITE,
        "bright_red": Colors.BRIGHT_RED,
        "bright_green": Colors.BRIGHT_GREEN,
        "bright_yellow": Colors.BRIGHT_YELLOW,
        "bright_blue": Colors.BRIGHT_BLUE,
        "bright_magenta": Colors.BRIGHT_MAGENTA,
        "bright_cyan": Colors.BRIGHT_CYAN,
    }

    result = text
    if bold:
        result = f"{Colors.BOLD}{result}"
    if fg and fg in color_map:
        result = f"{color_map[fg]}{result}"
    if bold or fg:
        result = f"{result}{Colors.RESET}"
    return result


def print_header(text: str) -> None:
    """Print a formatted header.

    Args:
        text: Header text.
    """
    print(f"\n{style(text, bold=True)}")
    print("=" * len(text))


def print_stats(entries: list[Any]) -> None:
    """Print statistics for entries.

    Args:
        entries: List of log entries.
    """

    if not entries:
        print("No entries to analyze.")
        return

    # Count by level
    level_counts: dict[str, int] = {}
    for entry in entries:
        level = entry.level.value if hasattr(entry, "level") else "unknown"
        level_counts[level] = level_counts.get(level, 0) + 1

    print_header("Statistics")
    print(f"  Total entries: {style(str(len(entries)), 'cyan', bold=True)}")

    for level_name in ("debug", "info", "success", "note", "warning", "error", "critical"):
        count = level_counts.get(level_name, 0)
        if count > 0:
            color = {
                "debug": "bright_cyan",
                "info": "blue",
                "success": "green",
                "note": "cyan",
                "warning": "yellow",
                "error": "red",
                "critical": "bright_red",
            }.get(level_name, "white")
            print(f"  {style(level_name.upper().ljust(10), fg=color)}: {count}")


def print_entry(entry: Any, show_fields: bool = False) -> None:
    """Print a single log entry.

    Args:
        entry: LogEntry to print.
        show_fields: Whether to show all fields.
    """
    from .utils import format_timestamp, parse_duration

    # Get level with color
    level = entry.level.value if hasattr(entry, "level") else "unknown"
    level_color = {
        "debug": "bright_cyan",
        "info": "blue",
        "success": "green",
        "note": "cyan",
        "warning": "yellow",
        "error": "red",
        "critical": "bright_red",
    }.get(level, "white")

    # Format timestamp
    ts_str = format_timestamp(entry.timestamp)

    # Get line number
    line_no = getattr(entry, "line_number", 0)
    line_str = f"[{line_no}]" if line_no > 0 else ""

    # Build output
    parts = [
        style(line_str, "bright_black") if line_str else "",
        style(ts_str, "dim"),
        style(level.upper().ljust(8), fg=level_color, bold=level in ("error", "critical")),
    ]

    # Add message
    if entry.message:
        parts.append(entry.message)

    # Add action info if available
    if hasattr(entry, "action_type") and entry.action_type:
        status = f" [{entry.action_status}]" if hasattr(entry, "action_status") and entry.action_status else ""
        parts.append(style(f"@{entry.action_type}{status}", "cyan"))

    # Add duration if available
    if hasattr(entry, "duration") and entry.duration is not None:
        parts.append(style(f"({parse_duration(entry.duration)})", "dim"))

    print("  ".join(str(p) for p in parts))

    # Show fields if requested
    if show_fields and hasattr(entry, "fields") and entry.fields:
        print(f"    {style('Fields:', 'dim')} {json.dumps(entry.fields, indent=2)}")


def export_json(entries: list[Any], output: str, pretty: bool = True) -> None:
    """Export entries to JSON file.

    Args:
        entries: List of log entries.
        output: Output file path.
        pretty: Pretty-print JSON.
    """
    data = [e.to_dict() if hasattr(e, "to_dict") else e for e in entries]
    with open(output, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)
    print(f"{style('✓', 'green')} Exported {len(entries)} entries to {style(output, 'bold')}")


def export_csv(entries: list[Any], output: str) -> None:
    """Export entries to CSV file.

    Args:
        entries: List of log entries.
        output: Output file path.
    """
    import csv

    if not entries:
        # Create empty file with headers
        with open(output, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([])
        return

    # Collect all field names
    fieldnames: set[str] = set()
    rows: list[dict[str, Any]] = []

    for entry in entries:
        row: dict[str, Any] = {
            "timestamp": entry.timestamp,
            "task_uuid": entry.task_uuid,
            "level": entry.level.value if hasattr(entry, "level") else "unknown",
            "message_type": entry.message_type,
            "message": entry.message or "",
            "action_type": entry.action_type or "",
            "action_status": entry.action_status.value if hasattr(entry, "action_status") and entry.action_status else "",
            "duration": entry.duration or "",
        }

        if hasattr(entry, "fields"):
            for key, value in entry.fields.items():
                if isinstance(value, (dict, list)):
                    row[f"field_{key}"] = json.dumps(value)
                else:
                    row[f"field_{key}"] = value

        fieldnames.update(row.keys())
        rows.append(row)

    # Write CSV
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer: csv.DictWriter[str] = csv.DictWriter(f, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(rows)

    print(f"{style('✓', 'green')} Exported {len(entries)} entries to {style(output, 'bold')}")


def export_html(entries: list[Any], output: str) -> None:
    """Export entries to HTML file.

    Args:
        entries: List of log entries.
        output: Output file path.
    """
    from .utils import format_timestamp, parse_duration

    # Build rows
    rows = []
    error_count = 0

    for entry in entries:
        if hasattr(entry, "is_error") and entry.is_error:
            error_count += 1

        # Format timestamp
        ts_str = format_timestamp(entry.timestamp)

        # Format duration
        duration_str = ""
        if hasattr(entry, "duration") and entry.duration is not None:
            duration_str = parse_duration(entry.duration)

        # Format fields
        fields_str = ""
        if hasattr(entry, "fields") and entry.fields:
            fields_str = f'<div class="fields"><pre>{json.dumps(entry.fields, indent=2)}</pre></div>'

        level_class = f"level-{entry.level.value}" if hasattr(entry, "level") else "level-info"

        row = f"""
                <tr>
                    <td class="timestamp">{ts_str}</td>
                    <td class="{level_class}">{entry.level.value.upper() if hasattr(entry, 'level') else 'INFO'}</td>
                    <td class="message">{entry.message or '-'}</td>
                    <td>{entry.action_type or '-'}</td>
                    <td>{duration_str}</td>
                    <td>{fields_str}</td>
                </tr>
            """
        rows.append(row)

    # HTML template
    html = f"""<!DOCTYPE html>
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
            <div class="stat"><span class="stat-label">Total:</span> <span class="stat-value">{len(entries)}</span></div>
            <div class="stat"><span class="stat-label">Errors:</span> <span class="stat-value">{error_count}</span></div>
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
                {''.join(rows)}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"{style('✓', 'green')} Exported {len(entries)} entries to {style(output, 'bold')}")


# ============================================================================
# Click-based CLI (if available)
# ============================================================================

if CLICK_AVAILABLE:
    @click.group()
    @click.version_option(version="0.1.0")
    def cli() -> None:
        """LogXPy Log Parser CLI - Query, analyze, and export LogXPy log files."""
        pass

    @cli.command("query")
    @click.argument("log_file", type=click.Path(exists=True, path_type=Path))
    @click.option("--level", "-l", multiple=True, help="Filter by log level(s)")
    @click.option("--message", "-m", help="Filter by message content")
    @click.option("--regex", "-r", is_flag=True, help="Use regex for message filtering")
    @click.option("--action", "-a", help="Filter by action type")
    @click.option("--task", "-t", help="Filter by task UUID")
    @click.option("--after", help="Filter entries after timestamp")
    @click.option("--before", help="Filter entries before timestamp")
    @click.option("--duration-min", type=float, default=0, help="Minimum duration in seconds")
    @click.option("--duration-max", type=float, default=float('inf'), help="Maximum duration in seconds")
    @click.option("--failed", is_flag=True, help="Show only failed actions")
    @click.option("--with-traceback", is_flag=True, help="Show only entries with traceback")
    @click.option("--limit", "-n", type=int, default=0, help="Limit number of results")
    @click.option("--sort", type=click.Choice(["timestamp", "level", "duration"]), default="timestamp", help="Sort by field")
    @click.option("--reverse", is_flag=True, help="Reverse sort order")
    @click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file (auto-detected format)")
    @click.option("--format", "-f", type=click.Choice(["json", "csv", "html"]), help="Output format")
    @click.option("--stats", is_flag=True, help="Show statistics")
    @click.option("--fields", is_flag=True, help="Show all fields")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    def query_cmd(
        log_file: Path,
        level: tuple[str, ...],
        message: str | None,
        regex: bool,
        action: str | None,
        task: str | None,
        after: str | None,
        before: str | None,
        duration_min: float,
        duration_max: float,
        failed: bool,
        with_traceback: bool,
        limit: int,
        sort: str,
        reverse: bool,
        output: Path | None,
        format: str | None,
        stats: bool,
        fields: bool,
        no_color: bool,
    ) -> None:
        """Query log file with filters and export results."""
        # Set NO_COLOR if requested
        if no_color:
            import os
            os.environ["NO_COLOR"] = "1"

        from .core import LogParser
        from .filter import LogEntries, LogFilter

        # Parse log file
        print_header(f"Querying: {log_file}")
        parser = LogParser(log_file)
        entries = parser.parse()

        # Show parse errors
        if parser.errors:
            print(f"\n{style('⚠', 'yellow')} Parse errors: {len(parser.errors)}")
            for error in parser.errors[:5]:
                print(f"  {style('!', 'red')} {error}")
            if len(parser.errors) > 5:
                print(f"  ... and {len(parser.errors) - 5} more")

        if not entries:
            print("No entries found.")
            return

        # Apply filters using LogFilter for chaining
        from .filter import LogFilter

        result = LogFilter(entries)

        if level:
            result = LogFilter(result.by_level(*level))
        if message:
            result = LogFilter(result.by_message(message, regex=regex))
        if action:
            result = LogFilter(result.by_action_type(action))
        if task:
            result = LogFilter(result.by_task_uuid(task))
        if after:
            result = LogFilter(result.after(float(after)))
        if before:
            result = LogFilter(result.before(float(before)))
        if duration_min > 0 or duration_max < float('inf'):
            result = LogFilter(result.by_duration(duration_min, duration_max))
        if failed:
            result = LogFilter(result.failed_actions())
        if with_traceback:
            result = LogFilter(result.with_traceback())

        # Sort
        filtered = result.sort(key=sort, reverse=reverse)

        # Limit
        if limit > 0:
            filtered = filtered.limit(limit)

        filtered_entries = list(filtered)

        print(f"  Matched {style(str(len(filtered_entries)), 'cyan', bold=True)} of {len(entries)} entries")

        # Export or print
        if output or format:
            # Determine format and output
            if output:
                output_ext = output.suffix.lstrip('.')
                export_format = format or output_ext
                output_path = str(output)
            else:
                export_format = format or "json"
                output_path = f"output.{export_format}"

            if export_format == "json":
                export_json(filtered_entries, output_path)
            elif export_format == "csv":
                export_csv(filtered_entries, output_path)
            elif export_format == "html":
                export_html(filtered_entries, output_path)
        else:
            # Print entries
            if stats:
                print_stats(filtered_entries)
            else:
                print_header(f"Results ({len(filtered_entries)})")
                for entry in filtered_entries[:100]:  # Limit print output
                    print_entry(entry, show_fields=fields)
                if len(filtered_entries) > 100:
                    print(f"\n  ... and {len(filtered_entries) - 100} more entries")

    @cli.command("analyze")
    @click.argument("log_file", type=click.Path(exists=True, path_type=Path))
    @click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for report")
    @click.option("--format", "-f", type=click.Choice(["text", "json", "html"]), default="text", help="Report format")
    @click.option("--slowest", "-s", type=int, default=10, help="Number of slowest actions to show")
    @click.option("--errors", is_flag=True, help="Show error analysis")
    @click.option("--actions", is_flag=True, help="Show action statistics")
    @click.option("--timeline", is_flag=True, help="Show timeline analysis")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    def analyze_cmd(
        log_file: Path,
        output: Path | None,
        format: str,
        slowest: int,
        errors: bool,
        actions: bool,
        timeline: bool,
        no_color: bool,
    ) -> None:
        """Analyze log file and generate report."""
        if no_color:
            import os
            os.environ["NO_COLOR"] = "1"

        from .analyzer import LogAnalyzer
        from .core import LogParser
        from .filter import LogEntries

        # Parse log file
        print_header(f"Analyzing: {log_file}")
        parser = LogParser(log_file)
        entries = parser.parse()

        if not entries:
            print("No entries to analyze.")
            return

        # Analyze
        analyzer = LogAnalyzer(LogEntries(entries))

        if errors:
            error_summary = analyzer.error_summary()
            print_header("Error Analysis")
            print(f"  Total errors: {style(str(error_summary.total_count), 'red', bold=True)}")
            print(f"  Unique types: {error_summary.unique_types}")
            if error_summary.most_common[0]:
                print(f"  Most common: {style(error_summary.most_common[0], 'yellow')} ({error_summary.most_common[1]}x)")

        if actions:
            print_header("Slowest Actions")
            for action_stat in analyzer.slowest_actions(slowest):
                print(f"  {style(action_stat.action_type, 'cyan')}: "
                      f"{style(f'{action_stat.mean_duration*1000:.2f}ms', 'yellow')} "
                      f"(avg over {action_stat.count} runs)")

        if timeline:
            print_header("Timeline")
            peak_periods = analyzer.peak_periods(5)
            from .utils import format_timestamp
            for period in peak_periods:
                print(f"  {format_timestamp(period.start)} - {format_timestamp(period.end)}: "
                      f"{style(str(period.entry_count), 'cyan')} entries")

        # Generate report
        report = analyzer.generate_report(format)

        if output:
            with open(output, "w") as f:
                f.write(report)
            print(f"\n{style('✓', 'green')} Report saved to {style(str(output), 'bold')}")
        elif format == "text":
            print(f"\n{report}")

    @cli.command("view")
    @click.argument("log_file", type=click.Path(exists=True, path_type=Path))
    @click.option("--level", "-l", multiple=True, help="Filter by log level(s)")
    @click.option("--follow", "-f", is_flag=True, help="Follow log file (like tail -f)")
    @click.option("--lines", "-n", type=int, default=50, help="Number of lines to show")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    def view_cmd(
        log_file: Path,
        level: tuple[str, ...],
        follow: bool,
        lines: int,
        no_color: bool,
    ) -> None:
        """View log file with colored output."""
        if no_color:
            import os
            os.environ["NO_COLOR"] = "1"

        from .filter import LogFilter
        from .monitor import LogFile

        logfile = LogFile.open(log_file)
        if logfile is None:
            print(f"{style('✗', 'red')} Failed to open log file")
            return

        if follow:
            # Follow mode
            print_header(f"Following: {log_file}")
            print("  Press Ctrl+C to stop\n")

            try:
                for entry in logfile.watch():
                    # Apply level filter
                    if level and entry.level.value not in level:
                        continue
                    print_entry(entry)
            except KeyboardInterrupt:
                print(f"\n{style('✓', 'green')} Stopped following")
        else:
            # Show recent lines
            entries = logfile.tail(lines)
            if level:
                entries = list(LogFilter(entries).by_level(*level))

            print_header(f"Viewing: {log_file} (last {len(entries)} lines)")
            for entry in entries:
                print_entry(entry)

    @cli.command("tree")
    @click.argument("log_file", type=click.Path(exists=True, path_type=Path))
    @click.option("--task", "-t", help="Task UUID to visualize")
    @click.option("--format", "-f", type=click.Choice(["ascii", "text"]), default="ascii", help="Output format")
    @click.option("--no-color", is_flag=True, help="Disable colored output")
    def tree_cmd(
        log_file: Path,
        task: str | None,
        format: str,
        no_color: bool,
    ) -> None:
        """Visualize task tree from log file."""
        if no_color:
            import os
            os.environ["NO_COLOR"] = "1"

        from .core import LogParser
        from .tree import TaskTree

        # Parse log file
        print_header(f"Building tree: {log_file}")
        parser = LogParser(log_file)
        entries = parser.parse()

        if not entries:
            print("No entries found.")
            return

        # Get task UUID
        if task:
            task_uuid = task
        else:
            # Use the task with the most entries (likely the main task)
            from collections import Counter
            task_counts = Counter(e.task_uuid for e in entries)
            if not task_counts:
                print("No task UUIDs found in log.")
                return
            task_uuid = task_counts.most_common(1)[0][0]
            print(f"  Using task UUID: {style(task_uuid, 'cyan')} ({task_counts[task_uuid]} entries)")

        # Build tree
        try:
            tree = TaskTree.from_entries(entries, task_uuid)
            print(tree.visualize(format))
        except ValueError as e:
            print(f"{style('✗', 'red')} {e}")


def main() -> int:
    """Main entry point for CLI.

    Returns:
        int: Exit code.
    """
    if not CLICK_AVAILABLE:
        print("Error: click is required for CLI functionality.")
        print("Install with: pip install logxy-log-parser[cli]")
        return 1

    try:
        cli()
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 130
    except Exception as e:
        print(f"{style('Error:', 'red')} {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
