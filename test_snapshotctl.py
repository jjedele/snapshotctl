"""Tests for get_n_time_windows_upto_reference."""

from datetime import datetime

import pytest

# The script has no .py extension — exec it into a namespace.
_ns = {}
exec(open("snapshotctl").read(), _ns)
get_windows = _ns["get_n_time_windows_upto_reference"]


def dt(s: str) -> datetime:
    """Shorthand: '2026-04-04 01:36' -> datetime."""
    return datetime.fromisoformat(s)


# ── Docstring examples ──────────────────────────────────────────────


class TestDocstringExamples:
    def test_hourly(self):
        result = get_windows(dt("2026-04-04 01:36"), 3, "h")
        assert result == [
            (dt("2026-04-03 23:00"), dt("2026-04-04 00:00")),
            (dt("2026-04-04 00:00"), dt("2026-04-04 01:00")),
            (dt("2026-04-04 01:00"), dt("2026-04-04 02:00")),
        ]

    def test_daily(self):
        result = get_windows(dt("2026-04-04 01:36"), 2, "d")
        assert result == [
            (dt("2026-04-03 00:00"), dt("2026-04-04 00:00")),
            (dt("2026-04-04 00:00"), dt("2026-04-05 00:00")),
        ]

    def test_weekly(self):
        result = get_windows(dt("2026-04-04 01:36"), 2, "w")
        assert result == [
            (dt("2026-03-23 00:00"), dt("2026-03-30 00:00")),
            (dt("2026-03-30 00:00"), dt("2026-04-06 00:00")),
        ]


# ── Single window (n=1) ─────────────────────────────────────────────


class TestSingleWindow:
    @pytest.mark.parametrize(
        "interval, expected_start, expected_end",
        [
            ("h", "2026-06-15 10:00", "2026-06-15 11:00"),
            ("d", "2026-06-15 00:00", "2026-06-16 00:00"),
            ("w", "2026-06-15 00:00", "2026-06-22 00:00"),  # Mon 15 Jun
            ("m", "2026-06-01 00:00", "2026-07-01 00:00"),
        ],
    )
    def test_n1(self, interval, expected_start, expected_end):
        result = get_windows(dt("2026-06-15 10:30"), 1, interval)
        assert result == [(dt(expected_start), dt(expected_end))]


# ── Hourly interval ─────────────────────────────────────────────────


class TestHourly:
    def test_reference_at_exact_hour(self):
        result = get_windows(dt("2026-04-04 03:00"), 2, "h")
        assert result == [
            (dt("2026-04-04 02:00"), dt("2026-04-04 03:00")),
            (dt("2026-04-04 03:00"), dt("2026-04-04 04:00")),
        ]

    def test_crossing_midnight(self):
        result = get_windows(dt("2026-04-04 01:15"), 4, "h")
        assert result == [
            (dt("2026-04-03 22:00"), dt("2026-04-03 23:00")),
            (dt("2026-04-03 23:00"), dt("2026-04-04 00:00")),
            (dt("2026-04-04 00:00"), dt("2026-04-04 01:00")),
            (dt("2026-04-04 01:00"), dt("2026-04-04 02:00")),
        ]

    def test_crossing_year_boundary(self):
        result = get_windows(dt("2026-01-01 00:30"), 3, "h")
        assert result == [
            (dt("2025-12-31 22:00"), dt("2025-12-31 23:00")),
            (dt("2025-12-31 23:00"), dt("2026-01-01 00:00")),
            (dt("2026-01-01 00:00"), dt("2026-01-01 01:00")),
        ]


# ── Daily interval ──────────────────────────────────────────────────


class TestDaily:
    def test_reference_at_midnight(self):
        result = get_windows(dt("2026-04-04 00:00"), 2, "d")
        assert result == [
            (dt("2026-04-03 00:00"), dt("2026-04-04 00:00")),
            (dt("2026-04-04 00:00"), dt("2026-04-05 00:00")),
        ]

    def test_crossing_month_boundary(self):
        result = get_windows(dt("2026-05-01 12:00"), 3, "d")
        assert result == [
            (dt("2026-04-29 00:00"), dt("2026-04-30 00:00")),
            (dt("2026-04-30 00:00"), dt("2026-05-01 00:00")),
            (dt("2026-05-01 00:00"), dt("2026-05-02 00:00")),
        ]

    def test_crossing_year_boundary(self):
        result = get_windows(dt("2026-01-01 08:00"), 3, "d")
        assert result == [
            (dt("2025-12-30 00:00"), dt("2025-12-31 00:00")),
            (dt("2025-12-31 00:00"), dt("2026-01-01 00:00")),
            (dt("2026-01-01 00:00"), dt("2026-01-02 00:00")),
        ]

    def test_leap_year_feb29(self):
        result = get_windows(dt("2028-02-29 10:00"), 2, "d")
        assert result == [
            (dt("2028-02-28 00:00"), dt("2028-02-29 00:00")),
            (dt("2028-02-29 00:00"), dt("2028-03-01 00:00")),
        ]

    def test_crossing_feb28_non_leap(self):
        result = get_windows(dt("2026-03-01 06:00"), 2, "d")
        assert result == [
            (dt("2026-02-28 00:00"), dt("2026-03-01 00:00")),
            (dt("2026-03-01 00:00"), dt("2026-03-02 00:00")),
        ]


# ── Weekly interval ──────────────────────────────────────────────────


class TestWeekly:
    def test_reference_on_monday(self):
        # 2026-04-06 is a Monday
        result = get_windows(dt("2026-04-06 09:00"), 2, "w")
        assert result == [
            (dt("2026-03-30 00:00"), dt("2026-04-06 00:00")),
            (dt("2026-04-06 00:00"), dt("2026-04-13 00:00")),
        ]

    def test_reference_on_sunday(self):
        # 2026-04-05 is a Sunday → week started Monday 2026-03-30
        result = get_windows(dt("2026-04-05 23:59"), 2, "w")
        assert result == [
            (dt("2026-03-23 00:00"), dt("2026-03-30 00:00")),
            (dt("2026-03-30 00:00"), dt("2026-04-06 00:00")),
        ]

    def test_crossing_year_boundary(self):
        # 2026-01-01 is a Thursday → week started Mon 2025-12-29
        result = get_windows(dt("2026-01-01 12:00"), 3, "w")
        assert result == [
            (dt("2025-12-15 00:00"), dt("2025-12-22 00:00")),
            (dt("2025-12-22 00:00"), dt("2025-12-29 00:00")),
            (dt("2025-12-29 00:00"), dt("2026-01-05 00:00")),
        ]

    def test_crossing_month_boundary(self):
        # 2026-05-04 is a Monday; reference exactly on boundary → anchor is May 4
        result = get_windows(dt("2026-05-04 00:00"), 2, "w")
        assert result == [
            (dt("2026-04-27 00:00"), dt("2026-05-04 00:00")),
            (dt("2026-05-04 00:00"), dt("2026-05-11 00:00")),
        ]


# ── Monthly interval ────────────────────────────────────────────────


class TestMonthly:
    def test_mid_month(self):
        result = get_windows(dt("2026-04-15 10:00"), 3, "m")
        assert result == [
            (dt("2026-02-01 00:00"), dt("2026-03-01 00:00")),
            (dt("2026-03-01 00:00"), dt("2026-04-01 00:00")),
            (dt("2026-04-01 00:00"), dt("2026-05-01 00:00")),
        ]

    def test_first_of_month(self):
        result = get_windows(dt("2026-04-01 00:00"), 2, "m")
        assert result == [
            (dt("2026-03-01 00:00"), dt("2026-04-01 00:00")),
            (dt("2026-04-01 00:00"), dt("2026-05-01 00:00")),
        ]

    def test_crossing_year_boundary(self):
        result = get_windows(dt("2026-01-20 08:00"), 3, "m")
        assert result == [
            (dt("2025-11-01 00:00"), dt("2025-12-01 00:00")),
            (dt("2025-12-01 00:00"), dt("2026-01-01 00:00")),
            (dt("2026-01-01 00:00"), dt("2026-02-01 00:00")),
        ]

    def test_crossing_into_february_non_leap(self):
        result = get_windows(dt("2026-02-15 12:00"), 2, "m")
        assert result == [
            (dt("2026-01-01 00:00"), dt("2026-02-01 00:00")),
            (dt("2026-02-01 00:00"), dt("2026-03-01 00:00")),
        ]

    def test_crossing_into_february_leap(self):
        result = get_windows(dt("2028-02-15 12:00"), 2, "m")
        assert result == [
            (dt("2028-01-01 00:00"), dt("2028-02-01 00:00")),
            (dt("2028-02-01 00:00"), dt("2028-03-01 00:00")),
        ]

    def test_twelve_months(self):
        result = get_windows(dt("2026-12-10 00:00"), 12, "m")
        assert len(result) == 12
        assert result[0] == (dt("2026-01-01 00:00"), dt("2026-02-01 00:00"))
        assert result[-1] == (dt("2026-12-01 00:00"), dt("2027-01-01 00:00"))
        for i in range(len(result) - 1):
            assert result[i][1] == result[i + 1][0]


# ── General properties ───────────────────────────────────────────────


class TestProperties:
    @pytest.mark.parametrize("interval", ["h", "d", "w", "m"])
    def test_windows_are_contiguous(self, interval):
        result = get_windows(dt("2026-06-15 14:30"), 5, interval)
        for i in range(len(result) - 1):
            assert result[i][1] == result[i + 1][0]

    @pytest.mark.parametrize("interval", ["h", "d", "w", "m"])
    def test_reference_inside_last_window(self, interval):
        ref = dt("2026-06-15 14:30")
        result = get_windows(ref, 3, interval)
        start, end = result[-1]
        assert start <= ref < end

    @pytest.mark.parametrize("interval", ["h", "d", "w", "m"])
    def test_window_starts_strictly_ascending(self, interval):
        result = get_windows(dt("2026-06-15 14:30"), 5, interval)
        starts = [w[0] for w in result]
        assert starts == sorted(starts)
        assert len(set(starts)) == len(starts)

    @pytest.mark.parametrize("interval", ["h", "d", "w", "m"])
    def test_each_window_has_positive_duration(self, interval):
        result = get_windows(dt("2026-06-15 14:30"), 5, interval)
        for start, end in result:
            assert end > start
