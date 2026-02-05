"""Tests for filter module."""

from __future__ import annotations

from calendar import timegm
from datetime import datetime

from logxpy_cli_view.filter import (
    UTC,
    _parse_timestamp,
    combine_filters_and,
    filter_by_end_date,
    filter_by_jmespath,
    filter_by_start_date,
    filter_by_uuid,
)


class TestFilterByJmespath:
    """Tests for filter_by_jmespath."""

    def test_no_match(self, sample_task):
        """Return False if the jmespath does not match."""
        filter_fn = filter_by_jmespath("action_type == `app:action`")
        assert filter_fn(sample_task) is False

    def test_match(self, sample_action_task):
        """Return True if the jmespath matches."""
        filter_fn = filter_by_jmespath("action_type == `app:action`")
        assert filter_fn(sample_action_task) is True


class TestFilterByUUID:
    """Tests for filter_by_uuid."""

    def test_no_match(self, sample_task):
        """Return False if UUID doesn't match."""
        filter_fn = filter_by_uuid("nope")
        assert filter_fn(sample_task) is False

    def test_match(self, sample_task):
        """Return True if UUID matches."""
        filter_fn = filter_by_uuid("cdeb220d-7605-4d5f-8341-1a170222e308")
        assert filter_fn(sample_task) is True


class TestParseTimestamp:
    """Tests for _parse_timestamp."""

    def test_returns_utc_datetime(self):
        """Returns a UTC datetime."""
        result = _parse_timestamp(1609459200)
        assert result.tzinfo is UTC
        assert result.year == 2021


class TestFilterByStartDate:
    """Tests for filter_by_start_date."""

    def test_no_match(self, sample_task):
        """Return False if timestamp is before start date."""
        now = datetime(2015, 10, 30, 22, 1, 15, tzinfo=UTC)
        task = dict(sample_task, timestamp=timegm(datetime(2015, 10, 30, 22, 1, 0).utctimetuple()))
        assert filter_by_start_date(now)(task) is False

    def test_match(self, sample_task):
        """Return True if timestamp is after start date."""
        now = datetime(2015, 10, 30, 22, 1, 15, tzinfo=UTC)
        task = dict(sample_task, timestamp=timegm(datetime(2015, 10, 30, 22, 2).utctimetuple()))
        assert filter_by_start_date(now)(task) is True

    def test_match_exact(self, sample_task):
        """Return True if timestamp equals start date."""
        now = datetime(2015, 10, 30, 22, 1, 15, tzinfo=UTC)
        task = dict(
            sample_task, timestamp=timegm(datetime(2015, 10, 30, 22, 1, 15).utctimetuple())
        )
        assert filter_by_start_date(now)(task) is True


class TestFilterByEndDate:
    """Tests for filter_by_end_date."""

    def test_no_match(self, sample_task):
        """Return False if timestamp is after end date."""
        now = datetime(2015, 10, 30, 22, 1, 15, tzinfo=UTC)
        task = dict(sample_task, timestamp=timegm(datetime(2015, 10, 30, 22, 2).utctimetuple()))
        assert filter_by_end_date(now)(task) is False

    def test_no_match_exact(self, sample_task):
        """Return False if timestamp equals end date."""
        now = datetime(2015, 10, 30, 22, 1, 15, tzinfo=UTC)
        task = dict(
            sample_task, timestamp=timegm(datetime(2015, 10, 30, 22, 1, 15).utctimetuple())
        )
        assert filter_by_end_date(now)(task) is False

    def test_match(self, sample_task):
        """Return True if timestamp is before end date."""
        now = datetime(2015, 10, 30, 22, 1, 15, tzinfo=UTC)
        task = dict(sample_task, timestamp=timegm(datetime(2015, 10, 30, 22, 1).utctimetuple()))
        assert filter_by_end_date(now)(task) is True


class TestCombineFiltersAnd:
    """Tests for combine_filters_and."""

    def test_all_true(self):
        """Return True if all filters pass."""
        combined = combine_filters_and(lambda x: True, lambda x: True)
        assert combined({}) is True

    def test_one_false(self):
        """Return False if any filter fails."""
        combined = combine_filters_and(lambda x: True, lambda x: False)
        assert combined({}) is False

    def test_no_filters(self):
        """Return True with no filters (vacuous truth)."""
        combined = combine_filters_and()
        assert combined({}) is True
