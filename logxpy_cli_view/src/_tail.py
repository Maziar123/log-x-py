"""Live tail mode for watching Eliot logs in real-time."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ._parse import tasks_from_iterable
from ._render import render_tasks
from ._stats import TaskStatistics


class LogTailer:
    """Watch log files for new entries and process them in real-time."""

    def __init__(
        self,
        file_path: Path | str,
        callback: Callable[[dict[str, Any]], None] | None = None,
        follow: bool = True,
        lines: int = 10,
    ):
        """
        Initialize log tailer.
        
        Args:
            file_path: Path to log file
            callback: Function to call for each new log entry
            follow: Keep watching for new entries
            lines: Number of lines to show initially
        """
        self.file_path = Path(file_path)
        self.callback = callback
        self.follow = follow
        self.lines = lines
        self._running = False
        self._file_position = 0

    def _read_new_lines(self) -> list[str]:
        """Read new lines from file since last position."""
        new_lines = []

        try:
            with open(self.file_path) as f:
                # Seek to last known position
                f.seek(self._file_position)

                # Read new lines
                for line in f:
                    line = line.strip()
                    if line:
                        new_lines.append(line)

                # Update position
                self._file_position = f.tell()
        except FileNotFoundError:
            pass

        return new_lines

    def _process_lines(self, lines: list[str]) -> None:
        """Process log lines."""
        for line in lines:
            try:
                entry = json.loads(line)
                if self.callback:
                    self.callback(entry)
            except json.JSONDecodeError:
                # Skip invalid JSON
                pass

    def tail(self) -> None:
        """Start tailing the log file."""
        self._running = True

        # Get initial file size for tail -n behavior
        if self.file_path.exists():
            with open(self.file_path) as f:
                all_lines = f.readlines()
                # Position at N lines from end
                start_line = max(0, len(all_lines) - self.lines)
                self._file_position = sum(len(l) for l in all_lines[:start_line])

        # Process initial lines
        initial_lines = self._read_new_lines()
        self._process_lines(initial_lines)

        if not self.follow:
            return

        # Follow mode: watch for new entries
        try:
            while self._running:
                new_lines = self._read_new_lines()
                if new_lines:
                    self._process_lines(new_lines)

                time.sleep(0.1)  # Poll interval
        except KeyboardInterrupt:
            self._running = False

    def stop(self) -> None:
        """Stop tailing."""
        self._running = False


def tail_logs(
    file_path: Path | str,
    follow: bool = True,
    lines: int = 10,
    write: Callable[[str], Any] = sys.stdout.write,
    **render_kwargs: Any,
) -> None:
    """
    Tail Eliot log files with real-time rendering.
    
    Args:
        file_path: Path to log file
        follow: Keep watching for new entries
        lines: Number of lines to show initially
        write: Output function
        **render_kwargs: Additional arguments for render_tasks
        
    Example:
        >>> tail_logs("app.log", follow=True, lines=20)
    """
    buffer: list[dict] = []

    def process_entry(entry: dict) -> None:
        buffer.append(entry)

        # Render immediately for single entries
        if len(buffer) == 1:
            tasks = tasks_from_iterable([entry])
            render_tasks(
                tasks=tasks,
                write=write,
                **render_kwargs
            )
            buffer.clear()

    tailer = LogTailer(
        file_path=file_path,
        callback=process_entry,
        follow=follow,
        lines=lines,
    )

    tailer.tail()


def watch_and_aggregate(
    file_path: Path | str,
    interval: int = 5,
    write: Callable[[str], Any] = sys.stdout.write,
) -> None:
    """
    Watch logs and periodically show aggregated statistics.
    
    Args:
        file_path: Path to log file
        interval: Aggregation interval in seconds
        write: Output function
        
    Example:
        >>> watch_and_aggregate("app.log", interval=10)
    """
    buffer: list[dict] = []
    last_stats_time = time.time()
    stats = TaskStatistics()

    def process_entry(entry: dict) -> None:
        nonlocal last_stats_time

        buffer.append(entry)
        stats.add_task(entry)

        # Show stats periodically
        if time.time() - last_stats_time >= interval:
            write(f"\n{'='*60}\n")
            write(f"📊 Stats (last {interval}s)\n")
            write(f"  Total: {stats.total_tasks}\n")
            write(f"  Success: {stats.successful_tasks} ({stats.success_rate:.1f}%)\n")
            write(f"  Failed: {stats.failed_tasks} ({stats.failure_rate:.1f}%)\n")

            if stats.durations:
                avg = sum(stats.durations) / len(stats.durations)
                write(f"  Avg Duration: {avg:.3f}s\n")

            write(f"{'='*60}\n\n")
            last_stats_time = time.time()

    tailer = LogTailer(
        file_path=file_path,
        callback=process_entry,
        follow=True,
        lines=0,  # Don't show initial lines in aggregate mode
    )

    write(f"📡 Watching {file_path} (stats every {interval}s)\n")
    write("Press Ctrl+C to stop\n\n")

    tailer.tail()


class LiveDashboard:
    """Simple live dashboard for log monitoring."""

    def __init__(
        self,
        file_path: Path | str,
        refresh_rate: float = 1.0,
    ):
        self.file_path = Path(file_path)
        self.refresh_rate = refresh_rate
        self.tailer = LogTailer(file_path, lines=0)
        self.stats = TaskStatistics()
        self.recent_tasks: list[dict] = []
        self.max_recent = 10

    def _clear_screen(self) -> None:
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")

    def _render_dashboard(self) -> None:
        """Render the dashboard."""
        self._clear_screen()

        print("=" * 70)
        print("📊 ELIOT LOG DASHBOARD")
        print("=" * 70)
        print(f"📁 File: {self.file_path}")
        print(f"🕐 Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Stats
        print("\n📈 STATISTICS")
        print("-" * 70)
        print(f"  Total tasks:    {self.stats.total_tasks}")
        print(f"  Success:        {self.stats.successful_tasks} ({self.stats.success_rate:.1f}%)")
        print(f"  Failed:         {self.stats.failed_tasks} ({self.stats.failure_rate:.1f}%)")

        if self.stats.durations:
            avg = sum(self.stats.durations) / len(self.stats.durations)
            max_d = max(self.stats.durations)
            print(f"  Avg duration:   {avg:.3f}s")
            print(f"  Max duration:   {max_d:.3f}s")

        # Recent errors
        if self.stats.error_types:
            print("\n❌ RECENT ERRORS")
            print("-" * 70)
            for error, count in self.stats.get_top_errors(3):
                print(f"  {error}: {count}")

        # Top action types
        if self.stats.action_types:
            print("\n📋 TOP ACTIONS")
            print("-" * 70)
            for action, count in self.stats.get_top_action_types(5):
                print(f"  {action}: {count}")

        # Recent tasks
        if self.recent_tasks:
            print("\n📝 RECENT TASKS")
            print("-" * 70)
            for task in self.recent_tasks[-5:]:
                action = task.get("action_type", "unknown")
                status = task.get("action_status", "?")
                duration = task.get("duration", "-")
                icon = "✓" if status == "succeeded" else "✗" if status == "failed" else "○"
                print(f"  {icon} {action} ({duration}s)")

        print("\n" + "=" * 70)
        print("Press Ctrl+C to exit")

    def run(self) -> None:
        """Run the live dashboard."""
        def process_entry(entry: dict) -> None:
            self.stats.add_task(entry)
            self.recent_tasks.append(entry)

            # Keep only recent tasks
            if len(self.recent_tasks) > self.max_recent:
                self.recent_tasks.pop(0)

        self.tailer.callback = process_entry
        self.tailer.follow = True
        self.tailer.lines = 0

        try:
            while True:
                # Read new lines
                new_lines = self.tailer._read_new_lines()
                self.tailer._process_lines(new_lines)

                # Render dashboard
                self._render_dashboard()

                time.sleep(self.refresh_rate)

        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")


__all__ = [
    "LiveDashboard",
    "LogTailer",
    "tail_logs",
    "watch_and_aggregate",
]
