__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import sys
import subprocess
import shutil
import glob
import logging
import platform
import toml

import typing as T

from pathlib import Path

import bmo.common

import typer


def _flatten_config_dict(conf, result, prefix="", *, sep="."):
    """{'a' : {'b' : 6}} -> { 'a.b' : 6 }"""
    if isinstance(conf, dict):
        for k, vals in conf.items():
            newkey = f"{prefix}{sep}{k}" if prefix else k
            _flatten_config_dict(vals, result, prefix=newkey, sep=sep)
    else:
        result[prefix] = conf


def flatten_config_dict(conf, sep="."):
    newdict = conf.copy()
    _flatten_config_dict(conf, newdict, sep=sep)
    return newdict


# Thanks https://github.com/tiangolo/typer/issues/86#issuecomment-996374166
def conf_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value:
        typer.echo(f"Loading config file {value}")
        with Path(value).open() as f:
            conf = toml.load(f)
            conf = flatten_config_dict(conf, sep="_")
        ctx.default_map = ctx.default_map or {}
        ctx.default_map.update(conf)
    return value


def hash256(msg: bytes) -> str:
    import hashlib

    return hashlib.sha256(msg).hexdigest()


def system() -> T.Tuple[str, str]:
    return (platform.system(), sys.platform)


def is_windows(cygwin_is_windows: bool = True) -> bool:
    """Check if we are running on windows.

    Parameters
    ----------
        cygwin_is_windows : (default `True`). When set to `True`, consider cygwin as Windows.

    Returns
    -------
    `True` if on Windows, `False` otherwise.
    """
    _sys = system()
    if _sys[0].startswith("windows"):
        return True
    return cygwin_is_windows and _sys[1] == "cygwin"


def find_program(
    name: str, hints: T.List[T.Union[Path, str]] = [], recursive: bool = False
) -> T.Optional[str]:
    """where is a given binary"""
    for hint in hints:
        hint = Path(hint).resolve()
        if not hint.exists():
            continue
        for p in glob.glob(f"{hint}/**/{name}", recursive=recursive):
            prg = shutil.which(p)
            if prg is not None:
                return prg
    return shutil.which(name)


def run_command(
    cmd: str, cwd: Path = Path.cwd(), silent: bool = False, stream: bool = True
) -> str:
    """Run a given command.

    Parameters
    ----------
    cmd : str
        cmd
    cwd : Path
        Current working directory.
    silent : bool
        If `True`, output is not printed onto console.
    stream : bool
        If `True` the output is printed line by line eagerly (as soon as a line is available)
        rather than all at once.

    Returns
    -------
    str

    Credits
    --------
    1. https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
    """
    logging.debug(f"Running `{cmd}` in {cwd}")
    p = subprocess.Popen(
        cmd.split(),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    lines = []
    if p.stdout is not None:
        for line in iter(p.stdout.readline, ""):
            if line is None:
                break
            line = line.rstrip()
            lines.append(f"> {line}")
            if stream and not silent:
                typer.echo(f"> {line}")

    output = "\n".join(lines)
    if not silent and not stream:
        typer.echo(f"> {output}")
    return output


def search_pat(pat, haystack):
    """Search for a pattern in haystack."""
    import re

    return re.search(pat, haystack, flags=re.IGNORECASE)


def success(msg: str):
    typer.echo(f":) {msg}")


def failure(msg: str):
    typer.echo(f":( {msg}")


def _test_run_command_linux():
    out = run_command("ls")
    out = run_command("ls -ltrh")
    return out


def test_common():
    if bmo.common.is_windows():
        return
    _test_run_command_linux()


def test_flatten_dict():
    d = dict(a=dict(b=dict(c=dict(d=5)), e=9), f=-1)
    d1 = flatten_config_dict(d)
    d2 = flatten_config_dict(d, "-")
    assert d1["a.b.c.d"] == d["a"]["b"]["c"]["d"]
    assert d2["a-b-c-d"] == d["a"]["b"]["c"]["d"]
    assert d1["f"] == d["f"]
    assert d2["f"] == d["f"]


if __name__ == "__main__":
    test_common()
    test_flatten_dict()
