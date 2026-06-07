import time

import pytest

from manen.exceptions import PollTimeoutException
from manen.helpers import poll, version, version_as_str


@pytest.mark.parametrize(
    "version_str,version_tuple",
    [
        ("1.2.3.4", (1, 2, 3, 4)),
        ("80.0.0.123", (80, 0, 0, 123)),
    ],
)
def test_create_version_w_4_parts(version_str, version_tuple):
    assert version(version_str) == version_tuple


@pytest.mark.parametrize(
    "version_str,version_tuple",
    [
        ("1.2.3", (1, 2, None, 3)),
        ("80.0.0", (80, 0, None, 0)),
    ],
)
def test_create_version_w_3_parts(version_str, version_tuple):
    assert version(version_str) == version_tuple


@pytest.mark.parametrize(
    "invalid_version",
    ["version", "1,2,3", "1.2.3.4.5", "1.0.a.1", "1..0.1"],
)
def test_invalid_version(invalid_version):
    with pytest.raises(ValueError):
        version(invalid_version)


@pytest.mark.parametrize(
    "invalid_version",
    [
        "1a2",
        "1a2b3",
        "1A2.3",
        "1 2.3",
        "1\t2.3",
        "1x2.3.4",
        "1.2x3",
        "1.2.3x4",
        "1.2.3.4x5",
        "1-2.3",
    ],
)
def test_invalid_version_with_non_dot_separator(invalid_version):
    """Regression test: the validation regex must reject inputs where the
    separator between numeric parts is not a literal dot. The previous regex
    used unescaped ``.`` which matched any character, letting invalid inputs
    slip through and trigger a confusing ``int()`` failure downstream.
    """
    with pytest.raises(ValueError):
        version(invalid_version)


@pytest.mark.parametrize(
    "version_1,version_2",
    [("1.0.0.0", "1.0.0.1"), ("0.1.0.0", "1.0.0.0"), ("2.0.0.1", "10.0.0.1")],
)
def test_versions_w_4_parts_comparison(version_1, version_2):
    assert version(version_1) < version(version_2)


@pytest.mark.parametrize(
    "version_1,version_2",
    [("1.0.0", "1.0.1"), ("0.1.0", "1.0.0"), ("2.0.1", "10.0.1")],
)
def test_versions_w_3_parts_comparison(version_1, version_2):
    assert version(version_1) < version(version_2)


# --- version_as_str ---


@pytest.mark.parametrize(
    "version_tuple,expected",
    [
        ((1, 2, 3, 4), "1.2.3.4"),
        ((80, 0, 0, 123), "80.0.0.123"),
        ((1, 2, None, 3), "1.2.None.3"),
    ],
)
def test_version_as_str_default_limit(version_tuple, expected):
    assert version_as_str(version_tuple) == expected


@pytest.mark.parametrize(
    "version_tuple,limit,expected",
    [
        ((1, 2, 3, 4), 1, "1"),
        ((1, 2, 3, 4), 2, "1.2"),
        ((1, 2, 3, 4), 3, "1.2.3"),
        ((1, 2, 3, 4), 4, "1.2.3.4"),
    ],
)
def test_version_as_str_custom_limit(version_tuple, limit, expected):
    assert version_as_str(version_tuple, limit=limit) == expected


def test_version_roundtrip():
    """``version_as_str`` followed by ``version`` should be the identity for
    well-formed 4-part versions."""
    original = (1, 2, 3, 4)
    assert version(version_as_str(original)) == original


# --- poll ---


def test_poll_returns_first_truthy_result():
    """A function that succeeds immediately should be called once and its
    result returned without sleeping."""
    calls = []

    def fn():
        calls.append(1)
        return "result"

    assert poll(fn, step=0.01, timeout=1) == "result"
    assert len(calls) == 1


def test_poll_retries_until_success():
    """If the function returns ``None`` initially, poll must keep calling
    until ``evaluate_success`` is truthy."""
    counter = {"n": 0}

    def fn():
        counter["n"] += 1
        return "ok" if counter["n"] >= 3 else None

    assert poll(fn, step=0.01, timeout=1) == "ok"
    assert counter["n"] == 3


def test_poll_raises_timeout_when_never_successful():
    """A function that always returns ``None`` must trigger
    ``PollTimeoutException`` once the timeout elapses."""
    with pytest.raises(PollTimeoutException, match="Timeout after"):
        poll(lambda: None, step=0.01, timeout=0.05)


def test_poll_passes_args_and_kwargs():
    """Positional and keyword arguments must be forwarded to the polled
    function."""

    def fn(a, b, c=None):
        return (a, b, c)

    result = poll(fn, args=(1, 2), kwargs={"c": 3}, step=0.01, timeout=1)
    assert result == (1, 2, 3)


def test_poll_with_no_args_or_kwargs():
    """Both ``args`` and ``kwargs`` default to empty when omitted."""
    assert poll(lambda: 42, step=0.01, timeout=1) == 42


def test_poll_custom_evaluate_success():
    """A custom ``evaluate_success`` predicate must override the default
    ``x is not None`` check (here: only positive numbers count as success)."""
    counter = {"n": -2}

    def fn():
        counter["n"] += 1
        return counter["n"]

    result = poll(
        fn,
        step=0.01,
        timeout=1,
        evaluate_success=lambda x: x > 0,
    )
    assert result == 1


def test_poll_respects_step_between_attempts():
    """The ``step`` argument should introduce a sleep between failed
    attempts (so two failures take at least one ``step`` of wall time)."""
    counter = {"n": 0}

    def fn():
        counter["n"] += 1
        return "ok" if counter["n"] >= 2 else None

    start = time.monotonic()
    poll(fn, step=0.05, timeout=1)
    elapsed = time.monotonic() - start
    assert elapsed >= 0.05
