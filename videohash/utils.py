import subprocess


def argstostr(args) -> str:
    return " ".join([f'"{x}"' if " " in x else x for x in args])


def runn(
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
    :param n: Number of commands to run in parallel per batch, defaults to 4. HAS TO BE A MULTIPLE OF, LESS THAN OR EQUAL TO `len(commands)`.
    :param raw: Do not byte-decode stdout and stderr (if captured).
    :return int: Count of non-zero returncodes.
    """
    succ = True
    outputs: list[str | bytes] = []
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
                if raw:
                    outputs.append((out or b"") + (err or b""))
                else:  # decode bytes to string
                    outputs.append(
                        (out or b"").decode(errors="ignore")
                        + (err or b"").decode(errors="ignore")
                    )
            else:
                if p.returncode:  # error
                    outputs.append(argstostr(p.args))
                    succ = False

    return succ, outputs
