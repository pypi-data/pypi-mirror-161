__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import requests
import tempfile
import logging
import sys

import typing as T
from pathlib import Path

import bmo.common

import typer

app = typer.Typer()


def determine_lang_tools(dir: Path) -> T.Dict[str, str]:
    """Find a suitable linter in the current directory."""
    res = dict()
    if (dir / "pyproject.toml") or (dir / "setup.py"):
        res["lang"] = "python"
        res["linter"] = "mypy"
    else:
        logging.warning("Failed to determine language and tooling.")
    return res


@app.command()
def mypy(sdir: Path = Path("src")):
    """Run mypy linter in given directory"""
    logging.info(f"Running mypy in {sdir}")
    assert sdir.exists(), "f{sdir} doesn't exists"
    bmo.common.run_command(
        f"{sys.executable} -m mypy --ignore-missing-imports --install-types --non-interactive {str(sdir)}"
    )


@app.command("gi")
def generate_gitignore(args: T.List[str] = [], force: bool = False):
    """Create gitignore file"""
    import requests

    cwd = Path.cwd().resolve()
    if not (cwd / ".git").exists():
        logging.warning(f"{cwd} is not a git repository?")

    gitignorefile = cwd / ".gitignore"

    if len(args) == 0:
        args = [determine_lang_tools(cwd).get("lang", "")]

    assert (
        len(args) > 0
    ), f"Could not automatically compute the API params.  Please pass using `--args` option."

    endpoint = ",".join(args)
    url = f"https://www.toptal.com/developers/gitignore/api/{endpoint}"
    logging.info(f"Fetching .gitignore content for {url}")

    res = requests.get(f"{url}")
    if not gitignorefile.exists() or force:
        with gitignorefile.open("w") as f:
            f.write(res.text)
        return

    typer.echo(res.text)
    logging.warning(
        f"{gitignorefile} exists. Use `--force` to overwrite. I am displaying the content of .gitignore to console."
    )


@app.command()
def lint(linter: str = "", dir: T.Optional[Path] = None):
    """Run a linter. If one is not given, pick one."""
    if dir is None:
        dir = Path.cwd()

    if not linter:
        linter = determine_lang_tools(dir).get("linter", "")
        logging.info(f"Automaticaly selecting linter '{linter}'")

    if linter == "mypy":
        mypy(dir)


@app.command("script")
def download_and_run_script(
    script: str, force: bool = False, download_only: bool = False
) -> str:
    """Download a script from https://gitlab.subcom.tech/open/scripts repo and execute it..

    Parameters
    ----------
    script : str
        The name or the full URL of the script.
    force : bool
        When set to `True`, redownload the script even if it exists in the cache.
    download_only:
        When set to `True`, only download the script and do not execute it.

    Returns
    -------
    `True` on success. `False` otherwise.

    """
    SCRIPT_DIR = Path(tempfile.gettempdir()) / "bmo"
    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    REPO_URL = "https://gitlab.subcom.tech/open/scripts/"

    if "https://" not in script[-10:] or "http://" not in script[-10:]:
        # Example: https://gitlab.subcom.tech/open/scripts/-/raw/main/bootstrap_debian.sh
        script = f"{REPO_URL}/-/raw/main/{script}"

    scriptname: str = script.rsplit("/", maxsplit=1)[-1]
    scriptpath = SCRIPT_DIR / scriptname
    if not scriptpath.exists() or force:
        res = requests.get(script)
        if res.status_code != 200:
            logging.warning(
                "Failed to download '{script}'. Please check the repository {REPO_URL}"
            )
            return ""
        with open(scriptpath, "w") as f:
            f.write(res.text)

    typer.echo(f"Writing script to {scriptpath}")
    if download_only:
        with scriptpath.open() as f:
            return f.read()

    logging.info(f"Executing {scriptpath}")
    output = bmo.common.run_command(f"bash {scriptpath}")
    return output


def test_download_only():
    text = download_and_run_script("bootstrap_debian.sh", download_only=True)
    assert len(text) > 0
    assert "downloads.docker.com" in text
    assert "node_exporter" in text


if __name__ == "__main__":
    app()
