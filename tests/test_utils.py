import sys

import pytest

from videohash.utils import runn


def _norm_lines(s: str | bytes) -> str | bytes:
    """Normalize Windows CRLF so asserts work cross-platform."""
    if isinstance(s, bytes):
        return s.replace(b"\r\n", b"\n")
    return s.replace("\r\n", "\n")


def test_runn_success_and_order():
    """Outputs must preserve command order even with dynamic scheduling."""
    cmds = [
        [sys.executable, "-c", "print('a')"],
        [sys.executable, "-c", "print('b')"],
        [sys.executable, "-c", "print('c')"],
    ]
    succ, outs = runn(cmds, n=2, getout=True)
    assert succ is True
    assert [_norm_lines(o) for o in outs] == ["a\n", "b\n", "c\n"]


def test_runn_empty():
    succ, outs = runn([], n=4)
    assert succ is True
    assert outs == []


def test_runn_failure():
    """Non-zero exit codes set succ=False but do not stop other commands."""
    cmds = [
        [sys.executable, "-c", "print('ok')"],
        [sys.executable, "-c", "import sys; sys.exit(1)"],
        [sys.executable, "-c", "print('also ok')"],
    ]
    succ, outs = runn(cmds, n=2, getout=True)
    assert succ is False
    assert _norm_lines(outs[0]) == "ok\n"
    assert _norm_lines(outs[2]) == "also ok\n"


def test_runn_raw():
    cmds = [[sys.executable, "-c", "print('hi')"]]
    succ, outs = runn(cmds, n=1, getout=True, raw=True)
    assert succ is True
    assert [_norm_lines(o) for o in outs] == [b"hi\n"]


def test_runn_propagates_exception():
    """Invalid commands must raise immediately, not hang or swallow."""
    with pytest.raises(FileNotFoundError):
        runn([["this_binary_does_not_exist_12345"]], n=1, getout=True)
