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


def test_runn_stderr_only():
    """geterr=True, getout=False must capture decoded stderr (used by videoduration)."""
    cmds = [
        [sys.executable, "-c", "import sys; print('err1', file=sys.stderr)"],
        [sys.executable, "-c", "import sys; print('err2', file=sys.stderr)"],
    ]
    succ, outs = runn(cmds, n=2, getout=False, geterr=True)
    assert succ is True
    assert _norm_lines(outs[0]) == "err1\n"
    assert _norm_lines(outs[1]) == "err2\n"


def test_runn_stdout_and_stderr():
    """getout=True, geterr=True concatenates stdout then stderr (used by cropdetect / ffmpeg -version)."""
    cmds = [
        [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr)",
        ],
    ]
    succ, outs = runn(cmds, n=1, getout=True, geterr=True)
    assert succ is True
    assert _norm_lines(outs[0]) == "out\nerr\n"


def test_runn_workers_exceed_commands():
    """n > len(commands) must not error and should still return correct outputs."""
    cmds = [
        [sys.executable, "-c", "print('x')"],
    ]
    succ, outs = runn(cmds, n=16, getout=True)
    assert succ is True
    assert _norm_lines(outs[0]) == "x\n"


def test_runn_propagates_exception():
    """Invalid commands must raise immediately, not hang or swallow."""
    with pytest.raises(FileNotFoundError):
        runn([["this_binary_does_not_exist_12345"]], n=1, getout=True)
