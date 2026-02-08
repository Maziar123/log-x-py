"""Tests for export functionality."""

from __future__ import annotations

import json

import pytest


class TestExport:
    """Tests for export functionality."""

    def test_export_to_json(self, sample_log_path: str, tmp_path: str) -> None:
        """Test exporting to JSON."""
        from logxy_log_parser import LogFilter, LogParser

        parser = LogParser(sample_log_path)
        logs = parser.parse()

        import os

        output_file = os.path.join(tmp_path, "output.json")
        LogFilter(logs).to_json(output_file)

        assert os.path.exists(output_file)

        with open(output_file) as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) > 0

    def test_export_to_csv(self, sample_log_path: str, tmp_path: str) -> None:
        """Test exporting to CSV."""
        from logxy_log_parser import LogFilter, LogParser

        parser = LogParser(sample_log_path)
        logs = parser.parse()

        import os

        output_file = os.path.join(tmp_path, "output.csv")
        LogFilter(logs).to_csv(output_file)

        assert os.path.exists(output_file)

        # Read CSV and verify
        with open(output_file) as f:
            content = f.read()

        assert "timestamp" in content
        assert "level" in content

    def test_export_to_html(self, sample_log_path: str, tmp_path: str) -> None:
        """Test exporting to HTML."""
        from logxy_log_parser import LogFilter, LogParser

        parser = LogParser(sample_log_path)
        logs = parser.parse()

        import os

        output_file = os.path.join(tmp_path, "output.html")
        LogFilter(logs).to_html(output_file)

        assert os.path.exists(output_file)

        with open(output_file) as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "</html>" in content

    def test_export_to_markdown(self, sample_log_path: str, tmp_path: str) -> None:
        """Test exporting to Markdown."""
        from logxy_log_parser import LogFilter, LogParser

        parser = LogParser(sample_log_path)
        logs = parser.parse()

        import os

        output_file = os.path.join(tmp_path, "output.md")
        LogFilter(logs).to_markdown(output_file)

        assert os.path.exists(output_file)

        with open(output_file) as f:
            content = f.read()

        assert "# Log Entries" in content
        assert "|" in content  # Markdown table

    def test_export_to_dataframe(self, sample_log_path: str) -> None:
        """Test exporting to pandas DataFrame."""
        from logxy_log_parser import LogFilter, LogParser

        parser = LogParser(sample_log_path)
        logs = parser.parse()

        df = LogFilter(logs).to_dataframe()

        assert df is not None
        assert len(df) > 0
        assert "timestamp" in df.columns or "level" in df.columns

    def test_export_empty_collection(self, tmp_path: str) -> None:
        """Test exporting empty collection."""
        from logxy_log_parser import LogEntries

        import os

        entries = LogEntries([])

        # Should not fail on empty collection
        json_file = os.path.join(tmp_path, "empty.json")
        entries.to_json(json_file)

        csv_file = os.path.join(tmp_path, "empty.csv")
        entries.to_csv(csv_file)
