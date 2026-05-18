import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor


def argstostr(args) -> str:
    return " ".join([f'"{x}"' if " " in x else x for x in args])


def runn_old(
    commands: list[list[str]] | list[str],
    n: int = 4,
    geterr=False,
    getout=False,
    raw=False,
) -> tuple[bool, list[str | bytes]]:
    """
    Run list of commands in batches of `n`. Aborts on any non-zero exit code.

    https://stackoverflow.com/a/71743719/9356410

    :param commands: List of commands to run as either arglists or strings.
    :param n: Number of commands to run in parallel per batch, defaults to 4.
    :param raw: Do not byte-decode stdout and stderr (if captured).
    :return int: Count of non-zero returncodes.
    """
    succ = True
    outputs: list[str | bytes] = []
    for j in range((len(commands) + n - 1) // n):
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
        try:
            for p in procs:
                out, err = p.communicate()

                if getout or geterr:
                    if raw:
                        outputs.append((out or b"") + (err or b""))
                    else:  # decode bytes to string
                        outputs.append(
                            (out or b"").decode(errors="ignore")
                            + (err or b"").decode(errors="ignore")
                        )
                else:
                    outputs.append(argstostr(p.args))

                if p.returncode != 0:
                    succ = False
        except BaseException:
            for p in procs:
                p.kill()
                p.wait()
            raise

    return succ, outputs


def _run_one(
    cmd,
    idx: int,
    getout: bool,
    geterr: bool,
    raw: bool,
    active_procs: list[subprocess.Popen],
    lock: threading.Lock,
) -> tuple[int, str | bytes, int]:
    """Run single command and return (index, output, returncode)."""
    p = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE if getout else None,
        stderr=subprocess.PIPE if geterr else None,
        text=False,
    )
    with lock:
        active_procs.append(p)
    out, err = p.communicate()

    if getout or geterr:
        if raw:
            output: str | bytes = (out or b"") + (err or b"")
        else:
            output = (out or b"").decode(errors="ignore") + (err or b"").decode(
                errors="ignore"
            )
    else:
        output = argstostr(p.args)

    return idx, output, p.returncode


def runn(
    commands: list[list[str]] | list[str],
    n: int = 4,
    geterr=False,
    getout=False,
    raw=False,
) -> tuple[bool, list[str | bytes]]:
    """
    Run list of commands with up to `n` concurrent workers.
    Aborts on any exception and kills all active subprocesses.
    Preserves output order.

    :param commands: List of commands to run as either arglists or strings.
    :param n: Maximum number of commands to run in parallel, default  4.
    :param raw: Do not byte-decode stdout and stderr (if captured).
    :return: (all_succeeded, outputs)
    """
    if not commands:
        return True, []

    active_procs: list[subprocess.Popen] = []
    lock = threading.Lock()
    outputs: list[str | bytes] = [None] * len(commands)  # type: ignore[assignment]
    succ = True

    try:
        with ThreadPoolExecutor(max_workers=n) as ex:
            futures = [
                ex.submit(
                    _run_one,
                    cmd,
                    i,
                    getout,
                    geterr,
                    raw,
                    active_procs,
                    lock,
                )
                for i, cmd in enumerate(commands)
            ]
            for f in futures:
                idx, output, rc = f.result()
                outputs[idx] = output
                if rc != 0:
                    succ = False
    except BaseException:
        with lock:
            procs = list(active_procs)
        for p in procs:
            try:
                p.kill()
                p.wait()
            except OSError:
                pass
        raise

    return succ, outputs
