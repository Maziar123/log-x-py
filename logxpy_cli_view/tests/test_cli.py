"""Tests for CLI module."""

from __future__ import annotations

import pytest

from logxpy_cli_view._cli import _decode_command_line, is_dark_terminal_background, main


class TestDecodeCommandLine:
    """Tests for _decode_command_line."""

    def test_decodes_bytes(self):
        """Decodes bytes to string."""
        result = _decode_command_line(b"hello")
        assert result == "hello"

    def test_passes_through_string(self):
        """Passes string through unchanged."""
        result = _decode_command_line("hello")
        assert result == "hello"


class TestIsDarkTerminalBackground:
    """Tests for is_dark_terminal_background."""

    def test_returns_default_when_no_colorfgbg(self, monkeypatch):
        """Returns default when COLORFGBG not set."""
        monkeypatch.delenv("COLORFGBG", raising=False)
        assert is_dark_terminal_background(default=True) is True
        assert is_dark_terminal_background(default=False) is False

    def test_dark_colorfgbg(self, monkeypatch):
        """Returns True for dark background codes."""
        monkeypatch.setenv("COLORFGBG", "0;0")
        assert is_dark_terminal_background() is True

    def test_light_colorfgbg(self, monkeypatch):
        """Returns False for light background codes."""
        monkeypatch.setenv("COLORFGBG", "0;7")
        assert is_dark_terminal_background() is False


class TestMain:
    """Tests for main function."""

    def test_version_flag(self, capsys):
        """--version prints version and exits."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "eliot-tree" in captured.out

    def test_help_flag(self, capsys):
        """--help prints help and exits."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Eliot log" in captured.out
