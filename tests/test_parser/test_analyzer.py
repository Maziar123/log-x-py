"""Tests for analyzer functionality."""

from __future__ import annotations

import pytest

from logxy_log_parser import LogAnalyzer, LogParser
from logxy_log_parser import ActionStatus


class TestLogAnalyzer:
    """Tests for LogAnalyzer class."""

    def test_init(self, sample_log_path: str) -> None:
        """Test initializing analyzer."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)

        assert analyzer is not None

    def test_error_summary(self, error_log_path: str) -> None:
        """Test error summary."""
        parser = LogParser(error_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        summary = analyzer.error_summary()

        assert summary.total_count > 0
        assert summary.unique_types > 0
        assert isinstance(summary.by_level, dict)
        assert isinstance(summary.by_action, dict)

    def test_error_patterns(self, error_log_path: str) -> None:
        """Test error patterns."""
        parser = LogParser(error_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        patterns = analyzer.error_patterns()

        assert len(patterns) > 0
        assert all(p.count > 0 for p in patterns)

    def test_slowest_actions(self, complex_log_path: str) -> None:
        """Test getting slowest actions."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        slowest = analyzer.slowest_actions(5)

        assert isinstance(slowest, list)
        assert len(slowest) <= 5

        # Should be sorted by duration
        if len(slowest) > 1:
            assert slowest[0].mean_duration >= slowest[1].mean_duration

    def test_fastest_actions(self, complex_log_path: str) -> None:
        """Test getting fastest actions."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        fastest = analyzer.fastest_actions(5)

        assert isinstance(fastest, list)
        assert len(fastest) <= 5

        # Should be sorted by duration (ascending)
        if len(fastest) > 1:
            assert fastest[0].mean_duration <= fastest[1].mean_duration

    def test_duration_by_action(self, complex_log_path: str) -> None:
        """Test duration statistics by action type."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        durations = analyzer.duration_by_action()

        assert isinstance(durations, dict)

        for action_type, stats in durations.items():
            assert stats.count >= 0
            assert stats.mean >= 0
            assert stats.min >= 0
            assert stats.max >= stats.min

    def test_deepest_nesting(self, complex_log_path: str) -> None:
        """Test getting deepest nesting level."""
        parser = LogParser(complex_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        deepest = analyzer.deepest_nesting()

        assert deepest >= 0

    def test_widest_tasks(self, sample_log_path: str) -> None:
        """Test getting widest tasks."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        widest = analyzer.widest_tasks()

        assert isinstance(widest, list)
        if widest:
            # Should be sorted by count (descending)
            assert all(widest[i][1] >= widest[i + 1][1] for i in range(len(widest) - 1))

    def test_failure_rate_by_action(self, sample_log_path: str) -> None:
        """Test failure rate calculation."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        rates = analyzer.failure_rate_by_action()

        assert isinstance(rates, dict)

        for action, rate in rates.items():
            assert 0.0 <= rate <= 1.0

    def test_most_common_errors(self, error_log_path: str) -> None:
        """Test getting most common errors."""
        parser = LogParser(error_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        errors = analyzer.most_common_errors(5)

        assert isinstance(errors, list)
        assert len(errors) <= 5
        assert all(isinstance(e, tuple) and len(e) == 2 for e in errors)

    def test_generate_text_report(self, sample_log_path: str) -> None:
        """Test generating text report."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        report = analyzer.generate_report("text")

        assert isinstance(report, str)
        assert len(report) > 0
        assert "Log Analysis Report" in report

    def test_generate_html_report(self, sample_log_path: str) -> None:
        """Test generating HTML report."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        report = analyzer.generate_report("html")

        assert isinstance(report, str)
        assert "<!DOCTYPE html>" in report
        assert "Log Analysis Report" in report

    def test_generate_json_report(self, sample_log_path: str) -> None:
        """Test generating JSON report."""
        import json

        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)
        report = analyzer.generate_report("json")

        assert isinstance(report, str)

        # Should be valid JSON
        data = json.loads(report)
        assert "total_entries" in data

    def test_unsupported_report_format(self, sample_log_path: str) -> None:
        """Test error on unsupported report format."""
        parser = LogParser(sample_log_path)
        logs = parser.parse()

        analyzer = LogAnalyzer(logs)

        with pytest.raises(ValueError):
            analyzer.generate_report("unsupported")
