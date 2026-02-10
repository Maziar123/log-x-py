"""Command-line interface for logxpy-cli-view."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from pprint import pformat
from typing import Any, TextIO

import iso8601
from . import (
    LogXPyParseError,
    EliotParseError,  # Backwards compatibility alias
    JSONParseError,
    combine_filters_and,
    filter_by_action_status,
    filter_by_action_type,
    filter_by_duration,
    filter_by_end_date,
    filter_by_field_exists,
    filter_by_jmespath,
    filter_by_keyword,
    filter_by_start_date,
    filter_by_task_level,
    filter_by_uuid,
    render_tasks,
    render_oneline,
    tasks_from_iterable,
)

from ._color import colored
from ._export import ExportOptions, export_tasks
from ._stats import calculate_statistics, print_statistics
from ._tail import LiveDashboard, tail_logs, watch_and_aggregate
from ._theme import ThemeMode, apply_theme_overrides, get_theme
from ._util import Writable


def text_writer(fd: TextIO) -> TextIO:
    """File writer that accepts Unicode to write."""
    return fd


def text_reader(fd: TextIO) -> TextIO:
    """File reader that returns Unicode from reading."""
    return fd


def parse_messages(
    files: list[TextIO] | None = None,
    select: list[str] | None = None,
    task_uuid: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    action_status: str | None = None,
    action_type: str | None = None,
    action_type_regex: bool = False,
    min_duration: float | None = None,
    max_duration: float | None = None,
    field_exists: list[str] | None = None,
    keyword: str | None = None,
    min_task_level: int | None = None,
    max_task_level: int | None = None,
) -> tuple[dict[str, int], Iterator[Any]]:
    """
    Parse message dictionaries from inputs into logxpy tasks.

    Args:
        files: List of file objects to read from
        select: JMESPath queries to filter tasks
        task_uuid: Specific task UUID to filter by
        start: Start date filter
        end: End date filter
        action_status: Filter by action status
        action_type: Filter by action type
        action_type_regex: Treat action_type as regex pattern
        min_duration: Minimum task duration
        max_duration: Maximum task duration
        field_exists: Fields that must exist
        keyword: Keyword to search for
        min_task_level: Minimum task level depth
        max_task_level: Maximum task level depth

    Returns:
        Tuple of (inventory dict mapping task_uuid to line_number, tasks iterator)
    """
    def filter_funcs() -> Iterator[Callable[[dict[str, Any]], bool]]:
        if task_uuid is not None:
            yield filter_by_uuid(task_uuid)
        if start:
            yield filter_by_start_date(start)
        if end:
            yield filter_by_end_date(end)
        if action_status:
            yield filter_by_action_status(action_status)
        if action_type:
            yield filter_by_action_type(action_type, regex=action_type_regex)
        if min_duration is not None or max_duration is not None:
            yield filter_by_duration(min_seconds=min_duration, max_seconds=max_duration)
        if field_exists:
            for field in field_exists:
                yield filter_by_field_exists(field)
        if keyword:
            yield filter_by_keyword(keyword)
        if min_task_level is not None or max_task_level is not None:
            yield filter_by_task_level(min_level=min_task_level, max_level=max_task_level)
        if select is not None:
            for query in select:
                yield filter_by_jmespath(query)

    def _parse(
        files: list[TextIO], inventory: dict[str, int]
    ) -> Iterator[dict[str, Any]]:
        for file in files:
            for line_number, line in enumerate(file, 1):
                try:
                    task: dict[str, Any] = json.loads(line)
                    # Map task_uuid to line_number
                    task_uuid = task.get("task_uuid")
                    if task_uuid:
                        inventory[str(task_uuid)] = line_number
                    yield task
                except Exception:
                    file_name = getattr(file, "name", "<unknown>")
                    raise JSONParseError(
                        file_name,
                        line_number,
                        line.rstrip("\n"),
                        sys.exc_info(),
                    )

    if not files:
        files = [text_reader(sys.stdin)]

    inventory: dict[str, int] = {}
    return inventory, tasks_from_iterable(
        filter(combine_filters_and(*filter_funcs()), _parse(files, inventory))
    )


def setup_platform(colorize: bool) -> None:
    """
    Set up any platform specifics for console output.

    Args:
        colorize: Whether color output is enabled
    """
    if platform.system() == "Windows":
        import warnings

        import win_unicode_console

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            win_unicode_console.enable()


def display_tasks(
    tasks: Iterable[Any],
    inventory: dict[str, int] | None,
    color: str,
    colorize_tree: bool,
    ascii: bool,
    theme_name: str,
    ignored_fields: list[str],
    field_limit: int,
    human_readable: bool,
    utc_timestamps: bool,
    theme_overrides: dict[str, Any] | None,
    show_line_numbers: bool = True,
    format: str = "tree",
) -> None:
    """
    Render Eliot tasks to stdout.

    Args:
        tasks: Tasks to render
        inventory: Mapping of task_uuid to line_number
        color: Color mode ('auto', 'always', 'never')
        colorize_tree: Whether to colorize tree lines
        ascii: Use ASCII characters for tree
        theme_name: Theme name ('auto', 'dark', 'light')
        ignored_fields: Fields to ignore
        field_limit: Truncation limit
        human_readable: Format values as human-readable
        utc_timestamps: Use UTC for timestamps
        theme_overrides: Theme override settings
        show_line_numbers: Whether to show line numbers in output
        format: Output format ('tree' or 'oneline')
    """
    if color == "auto":
        colorize = sys.stdout.isatty()
    else:
        colorize = color == "always"

    setup_platform(colorize=colorize)
    write: Writable = sys.stdout.write
    write_err: Writable = sys.stderr.write

    # Map theme_name to ThemeMode
    theme_mode = ThemeMode.AUTO
    if theme_name == "dark":
        theme_mode = ThemeMode.DARK
    elif theme_name == "light":
        theme_mode = ThemeMode.LIGHT

    if theme_mode == ThemeMode.AUTO:
        dark_background = is_dark_terminal_background(default=True)
    else:
        dark_background = theme_mode == ThemeMode.DARK

    theme = apply_theme_overrides(
        get_theme(
            dark_background=dark_background,
            colored=colored if colorize else None,
        ),
        theme_overrides or {},
    )

    if format == "oneline":
        render_oneline(
            tasks=tasks,
            theme=theme,
            write=write,
        )
        return

    render_tasks(
        write=write,
        write_err=write_err,
        tasks=tasks,
        inventory=inventory or {},
        ignored_fields=set(ignored_fields) or None,
        field_limit=field_limit,
        human_readable=human_readable,
        colorize_tree=colorize and colorize_tree,
        ascii=ascii,
        utc_timestamps=utc_timestamps,
        theme=theme,
        show_line_numbers=show_line_numbers,
    )


def _decode_command_line(value: str | bytes, encoding: str = "utf-8") -> str:
    """
    Decode a command-line argument.

    Args:
        value: Value to decode
        encoding: Encoding to use

    Returns:
        Decoded string
    """
    if isinstance(value, bytes):
        return value.decode(encoding)
    return value


def is_dark_terminal_background(default: bool = True) -> bool:
    """
    Check if the terminal uses a dark background color.

    Currently checks the COLORFGBG environment variable.

    Args:
        default: Default value if unable to determine

    Returns:
        True if dark background, False otherwise
    """
    colorfgbg = os.environ.get("COLORFGBG")
    if colorfgbg is not None:
        parts = colorfgbg.split(";")
        try:
            last_number = int(parts[-1])
            if 0 <= last_number <= 6 or last_number == 8:
                return True
            else:
                return False
        except ValueError:
            pass
    return default


# Config paths using pathlib
CONFIG_PATHS: list[Path] = [
    Path.home() / ".config" / "eliot-tree2" / "config.json",
]


def locate_config() -> Path | None:
    """Find the first config search path that exists."""
    return next((path for path in CONFIG_PATHS if path.exists()), None)


def read_config(path: Path | str | None) -> dict[str, Any]:
    """Read a config file from the specified path."""
    if path is None:
        return {}
    if isinstance(path, str):
        path = Path(path)
    with path.open("rb") as fd:
        return json.load(fd)


CONFIG_BLACKLIST: set[str] = {
    "files",
    "start",
    "end",
    "print_default_config",
    "config",
    "select",
    "task_uuid",
    "action_status",
    "action_type",
    "action_type_regex",
    "min_duration",
    "max_duration",
    "field_exists",
    "keyword",
    "min_task_level",
    "max_task_level",
    "func",  # argparse subcommand
}


def print_namespace(namespace: argparse.Namespace) -> None:
    """Print an argparse namespace to stdout as JSON."""
    config = {
        k: v for k, v in vars(namespace).items() if k not in CONFIG_BLACKLIST
    }
    stdout = text_writer(sys.stdout)
    stdout.write(json.dumps(config, indent=2))


@dataclass(frozen=True, slots=True)
class CLIOptions:
    """Dataclass for CLI options."""

    files: list[TextIO] = field(default_factory=list)
    config: str | None = None
    task_uuid: str | None = None
    ignored_fields: list[str] = field(default_factory=list)
    human_readable: bool = True
    utc_timestamps: bool = True
    color: str = "auto"
    ascii: bool = False
    colorize_tree: bool = True
    theme_name: str = "auto"
    field_limit: int = 100
    select: list[str] | None = None
    start: Any = None
    end: Any = None
    print_default_config: bool = False
    print_current_config: bool = False


def cmd_render(args: argparse.Namespace) -> int:
    """Handle render command."""
    stderr = text_writer(sys.stderr)

    try:
        inventory, tasks = parse_messages(
            files=args.files,
            select=args.select,
            task_uuid=args.task_uuid,
            start=args.start,
            end=args.end,
            action_status=args.action_status,
            action_type=args.action_type,
            action_type_regex=args.action_type_regex,
            min_duration=args.min_duration,
            max_duration=args.max_duration,
            field_exists=args.field_exists or None,
            keyword=args.keyword,
            min_task_level=args.min_task_level,
            max_task_level=args.max_task_level,
        )

        config = read_config(locate_config() or args.config)

        display_tasks(
            tasks=tasks,
            inventory=inventory,
            color=args.color,
            colorize_tree=args.colorize_tree,
            theme_name=args.theme_name,
            ascii=args.ascii,
            ignored_fields=args.ignored_fields,
            field_limit=args.field_limit,
            human_readable=args.human_readable,
            utc_timestamps=args.utc_timestamps,
            theme_overrides=config.get("theme_overrides"),
            show_line_numbers=args.show_line_numbers,
            format=args.format,
        )
    except JSONParseError as e:
        stderr.write(
            f"JSON parse error, file {e.file_name}, line {e.line_number}:\n"
            f"{e.line}\n\n"
        )
        raise e.exc_info[1].with_traceback(e.exc_info[2])
    except EliotParseError as e:
        # Get task_uuid from message_dict for error reporting
        task_uuid = e.message_dict.get("task_uuid")
        if task_uuid and task_uuid in inventory:
            line_number = inventory[task_uuid]
            stderr.write(
                f"LogXPy message parse error, line {line_number}:\n"
                f"{pformat(e.message_dict)}\n\n"
            )
        else:
            stderr.write(
                f"LogXPy message parse error:\n"
                f"{pformat(e.message_dict)}\n\n"
            )
        raise e.exc_info[1].with_traceback(e.exc_info[2])

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Handle stats command."""

    # Load all tasks as dicts for stats
    tasks = []
    for file in args.files or [sys.stdin]:
        for line in file:
            line = line.strip()
            if line:
                try:
                    tasks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    stats = calculate_statistics(tasks)
    print_statistics(stats)

    # Export to JSON if requested
    if args.output:
        import json as json_module
        data = {
            "total_tasks": stats.total_tasks,
            "successful_tasks": stats.successful_tasks,
            "failed_tasks": stats.failed_tasks,
            "success_rate": stats.success_rate,
            "failure_rate": stats.failure_rate,
            "duration_stats": stats.duration_stats,
            "action_types": dict(stats.action_types),
            "error_types": dict(stats.error_types),
        }
        with open(args.output, "w") as f:
            json_module.dump(data, f, indent=2)
        print(f"\n📁 Statistics exported to: {args.output}")

    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Handle export command."""
    from ._parse import tasks_from_iterable

    # Load tasks
    tasks = []
    for file in args.files or [sys.stdin]:
        for line in file:
            line = line.strip()
            if line:
                try:
                    tasks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    parsed_tasks = list(tasks_from_iterable(tasks))

    options = ExportOptions(
        indent=args.indent if args.format == "json" else None,
        include_fields=args.include_fields,
        exclude_fields=args.exclude_fields,
    )

    count = export_tasks(
        tasks=parsed_tasks,
        output=args.output,
        format=args.format,
        options=options,
        title=args.title if args.format == "html" else None,
    )

    print(f"📁 Exported {count} tasks to {args.output} ({args.format})")
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    """Handle tail command."""
    if not args.files:
        print("Error: tail command requires a file path", file=sys.stderr)
        return 1

    file_path = args.files[0].name if hasattr(args.files[0], "name") else args.files[0]

    if args.dashboard:
        dashboard = LiveDashboard(file_path, refresh_rate=args.refresh)
        dashboard.run()
    elif args.aggregate:
        watch_and_aggregate(file_path, interval=args.interval)
    else:
        tail_logs(
            file_path=file_path,
            follow=args.follow,
            lines=args.lines,
            human_readable=args.human_readable,
            field_limit=args.field_limit,
        )

    return 0


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="logxpy-view",
        description="Render and analyze logxpy logs as ASCII trees.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__import__('logxpy_cli_view').__version__}",
        help="Show version and exit.",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        dest="config",
        default=None,
        help="File to read configuration options from.",
    )
    parser.add_argument(
        "--show-default-config",
        dest="print_default_config",
        action="store_true",
        help="Show the default configuration.",
    )
    parser.add_argument(
        "--show-current-config",
        dest="print_current_config",
        action="store_true",
        help="Show the current effective configuration.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Render command (default)
    render_parser = subparsers.add_parser(
        "render",
        aliases=["r", "show"],
        help="Render logs as ASCII tree (default)",
    )
    render_parser.set_defaults(func=cmd_render)

    _add_common_args(render_parser)
    _add_filter_args(render_parser)
    _add_render_args(render_parser)

    # Stats command
    stats_parser = subparsers.add_parser(
        "stats",
        aliases=["s", "statistics"],
        help="Show statistics and analytics",
    )
    stats_parser.set_defaults(func=cmd_stats)
    _add_common_args(stats_parser)
    stats_parser.add_argument(
        "-o", "--output",
        help="Export statistics to JSON file",
    )

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        aliases=["e", "convert"],
        help="Export logs to various formats",
    )
    export_parser.set_defaults(func=cmd_export)
    _add_common_args(export_parser)
    export_parser.add_argument(
        "-f", "--format",
        choices=["json", "csv", "html", "logfmt"],
        required=True,
        help="Export format",
    )
    export_parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path",
    )
    export_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level",
    )
    export_parser.add_argument(
        "--include-fields",
        nargs="+",
        help="Fields to include (default: all)",
    )
    export_parser.add_argument(
        "--exclude-fields",
        nargs="+",
        help="Fields to exclude",
    )
    export_parser.add_argument(
        "--title",
        default="Eliot Log Export",
        help="HTML page title",
    )

    # Tail command
    tail_parser = subparsers.add_parser(
        "tail",
        aliases=["t", "watch", "follow"],
        help="Watch logs in real-time",
    )
    tail_parser.set_defaults(func=cmd_tail)
    _add_common_args(tail_parser)
    tail_parser.add_argument(
        "-n", "--lines",
        type=int,
        default=10,
        help="Number of lines to show initially",
    )
    tail_parser.add_argument(
        "-f", "--follow",
        action="store_true",
        default=True,
        help="Follow file for new entries",
    )
    tail_parser.add_argument(
        "--no-follow",
        dest="follow",
        action="store_false",
        help="Don't follow file",
    )
    tail_parser.add_argument(
        "-d", "--dashboard",
        action="store_true",
        help="Show live dashboard",
    )
    tail_parser.add_argument(
        "-a", "--aggregate",
        action="store_true",
        help="Show periodic statistics",
    )
    tail_parser.add_argument(
        "-i", "--interval",
        type=int,
        default=5,
        help="Aggregation interval in seconds",
    )
    tail_parser.add_argument(
        "-r", "--refresh",
        type=float,
        default=1.0,
        help="Dashboard refresh rate in seconds",
    )

    return parser


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to parser."""
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        type=argparse.FileType("r"),
        help="Files to process. Omit to read from stdin.",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        dest="config",
        help="File to read configuration options from.",
    )


def _add_filter_args(parser: argparse.ArgumentParser) -> None:
    """Add filter arguments to parser."""
    filter_group = parser.add_argument_group("Filtering Options")

    filter_group.add_argument(
        "-u",
        "--task-uuid",
        dest="task_uuid",
        metavar="UUID",
        type=_decode_command_line,
        help="Select a specific task by UUID.",
    )
    filter_group.add_argument(
        "--select",
        action="append",
        metavar="QUERY",
        dest="select",
        type=_decode_command_line,
        help="Select tasks based on a jmespath query. Can be used multiple times.",
    )
    filter_group.add_argument(
        "--start",
        dest="start",
        type=iso8601.parse_date,
        help="Select tasks after an ISO8601 date.",
    )
    filter_group.add_argument(
        "--end",
        dest="end",
        type=iso8601.parse_date,
        help="Select tasks before an ISO8601 date.",
    )
    filter_group.add_argument(
        "--status",
        dest="action_status",
        choices=["started", "succeeded", "failed"],
        help="Filter by action status.",
    )
    filter_group.add_argument(
        "--action-type",
        dest="action_type",
        metavar="PATTERN",
        help="Filter by action type (supports regex with --action-type-regex).",
    )
    filter_group.add_argument(
        "--action-type-regex",
        dest="action_type_regex",
        action="store_true",
        default=False,
        help="Treat --action-type as a regex pattern.",
    )
    filter_group.add_argument(
        "--min-duration",
        dest="min_duration",
        type=float,
        metavar="SECONDS",
        help="Filter tasks with duration >= SECONDS.",
    )
    filter_group.add_argument(
        "--max-duration",
        dest="max_duration",
        type=float,
        metavar="SECONDS",
        help="Filter tasks with duration <= SECONDS.",
    )
    filter_group.add_argument(
        "--has-field",
        dest="field_exists",
        action="append",
        default=[],
        metavar="FIELD",
        help="Filter tasks that have FIELD. Use dot notation for nested fields.",
    )
    filter_group.add_argument(
        "--keyword",
        dest="keyword",
        metavar="KEYWORD",
        help="Filter tasks containing KEYWORD in any field.",
    )
    filter_group.add_argument(
        "--min-level",
        dest="min_task_level",
        type=int,
        metavar="N",
        help="Filter tasks at level >= N (1 = top level).",
    )
    filter_group.add_argument(
        "--max-level",
        dest="max_task_level",
        type=int,
        metavar="N",
        help="Filter tasks at level <= N.",
    )


def _add_render_args(parser: argparse.ArgumentParser) -> None:
    """Add render-specific arguments to parser."""
    display_group = parser.add_argument_group("Display Options")

    display_group.add_argument(
        "-i",
        "--ignore-task-key",
        action="append",
        default=[],
        dest="ignored_fields",
        metavar="KEY",
        type=_decode_command_line,
        help="Ignore a task key. Use multiple times to ignore multiple keys.",
    )
    display_group.add_argument(
        "--raw",
        action="store_false",
        dest="human_readable",
        help="Do not format values as human-readable.",
    )
    display_group.add_argument(
        "--local-timezone",
        action="store_false",
        dest="utc_timestamps",
        help="Convert timestamps to the local timezone.",
    )
    display_group.add_argument(
        "--color",
        default="auto",
        choices=["always", "auto", "never"],
        dest="color",
        help="Color the output. Defaults based on whether output is a TTY.",
    )
    display_group.add_argument(
        "--ascii",
        action="store_true",
        default=False,
        dest="ascii",
        help="Use ASCII for tree drawing characters.",
    )
    display_group.add_argument(
        "--no-color-tree",
        action="store_false",
        default=True,
        dest="colorize_tree",
        help="Do not color the tree lines.",
    )
    display_group.add_argument(
        "--theme",
        default="auto",
        choices=["auto", "dark", "light"],
        dest="theme_name",
        help="Select a color theme to use.",
    )
    display_group.add_argument(
        "-l",
        "--field-limit",
        metavar="LENGTH",
        type=int,
        default=100,
        dest="field_limit",
        help="Limit field value length. Use 0 for no limit.",
    )
    display_group.add_argument(
        "--no-line-numbers",
        dest="show_line_numbers",
        action="store_false",
        default=True,
        help="Hide line numbers in the tree output.",
    )
    display_group.add_argument(
        "--format",
        choices=["tree", "oneline"],
        default="oneline",
        dest="format",
        help="Output format: oneline (default) or tree.",
    )


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for eliot-tree CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_argument_parser()
    args = parser.parse_args(argv)

    # Handle config display options first (before checking for files)
    if args.print_default_config:
        print_namespace(parser.parse_args([]))
        return 0

    # Read config for --print-current-config
    if args.print_current_config:
        config_path = args.config
        if config_path is None:
            located = locate_config()
            config_path = str(located) if located else None
        config = read_config(config_path)
        parser.set_defaults(**config)
        args = parser.parse_args(argv)
        print_namespace(args)
        return 0

    # Handle legacy mode (no subcommand, just render)
    if args.command is None:
        # For legacy mode, files are passed directly without a subcommand
        # Treat remaining args as files
        if argv and all(not arg.startswith('-') for arg in argv):
            # Re-parse with render subcommand
            argv = ['render'] + argv
            args = parser.parse_args(argv)
            return args.func(args)
        else:
            parser.print_help()
            return 0

    # Read config and re-parse for normal commands
    config_path = args.config
    if config_path is None:
        located = locate_config()
        config_path = str(located) if located else None

    config = read_config(config_path)
    parser.set_defaults(**config)
    args = parser.parse_args(argv)

    # Execute command
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
