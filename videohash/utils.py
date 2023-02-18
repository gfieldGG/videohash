from pathlib import Path
import tempfile
import subprocess
import uuid

import numpy as np


def get_tempdir(basedir: Path = None) -> Path:
    base: Path = basedir or Path(tempfile.gettempdir())
    tempdir = base / f"vh-{uuid.uuid4()}"
    if not tempdir.exists():
        tempdir.mkdir(parents=True, exist_ok=False)

    return tempdir


def get_files_in_dir(directory: Path) -> list[Path]:
    return sorted([f for f in directory.iterdir() if f.is_file()])


def argstostr(args) -> str:
    return " ".join([f'"{x}"' if " " in x else x for x in args])


def runn(
    commands: list[list[str]] | list[str], n: int = 4, geterr=False, getout=False
) -> tuple[bool, list[str]]:
    """
    Run list of commands in batches of `n`. Aborts on any non-zero exit code.

    https://stackoverflow.com/a/71743719/9356410

    :param commands: List of commands to run as either arglists or strings.
    :param n: Number of commands to run in parallel per batch, defaults to 4. HAS TO BE A MULTIPLE OF, LESS THAN OR EQUAL TO `len(commands)`.
    :return int: Count of non-zero returncodes.
    """
    succ = True
    outputs = []
    for j in range(max(int(len(commands) / n), 1)):
        procs = [
            subprocess.Popen(
                i,
                shell=False,
                stdout=subprocess.PIPE if getout else None,
                stderr=subprocess.PIPE if geterr else None,
                text=False,
            )
            for i in commands[j * n : min((j + 1) * n, len(commands))]
        ]
        for p in procs:
            out, err = p.communicate()

            if getout or geterr:
                outputs.append(
                    (out or b"").decode(errors="ignore")
                    + (err or b"").decode(errors="ignore")
                )

            if p.returncode:  # error
                if not getout or geterr:
                    outputs.append(argstostr(p.args))
                succ = False

    return True, outputs


def to_bitstring(i: int) -> str:
    return format(i, "064b")


def to_int(s: str) -> int:
    return int(s, 2)


def hamming(sa, sb) -> int:
    if not isinstance(sa, str):
        sa = to_bitstring(sa)
    if not isinstance(sb, str):
        sb = to_bitstring(sb)

    _bitlist_a = list(map(int, sa.replace("0b", "")))
    _bitlist_b = list(map(int, sb.replace("0b", "")))
    return len(
        np.bitwise_xor(
            _bitlist_a,
            _bitlist_b,
        ).nonzero()[0]
    )
