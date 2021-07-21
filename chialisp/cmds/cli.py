import click
import pytest
import os
import io
import shutil
from pathlib import Path

from chialisp import __version__

from chia.util.bech32m import encode_puzzle_hash, decode_puzzle_hash

from chialisp.cmds import (
    clsp,
)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

def monkey_patch_click() -> None:
    # this hacks around what seems to be an incompatibility between the python from `pyinstaller`
    # and `click`
    #
    # Not 100% sure on the details, but it seems that `click` performs a check on start-up
    # that `codecs.lookup(locale.getpreferredencoding()).name != 'ascii'`, and refuses to start
    # if it's not. The python that comes with `pyinstaller` fails this check.
    #
    # This will probably cause problems with the command-line tools that use parameters that
    # are not strict ascii. The real fix is likely with the `pyinstaller` python.

    import click.core

    click.core._verify_python3_env = lambda *args, **kwargs: 0  # type: ignore


@click.group(
    help=f"\n  Dev tooling for Chialisp development \n",
    epilog="Make a new directory and try chialisp init",
    context_settings=CONTEXT_SETTINGS,
)

@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.ensure_object(dict)

@cli.command("version", short_help="Show chialisp version")
def version_cmd() -> None:
    print(__version__)

@cli.command("test", short_help="Run the local test suite (located in ./tests)")
@click.option("-d", "--discover", is_flag=True, type=bool, help="List the tests without running them")
@click.option("-i","--init", is_flag=True, type=bool, help="Create the test directory and/or add a new skeleton test")
def test_cmd(discover: bool, init: str):
    if init:
        test_dir = Path(os.getcwd()).joinpath("tests")
        if not test_dir.exists():
            os.mkdir("tests")
        import chialisp.test as testlib
        src_path = Path(testlib.__file__).parent.joinpath("skeleton.py")
        dest_path = test_dir.joinpath("skeleton.py")
        shutil.copyfile(src_path, dest_path)
    if discover:
        pytest.main(["--collect-only","./tests"])
    elif not init:
        pytest.main(["./tests"])

@cli.command("encode", short_help="Encode a puzzle hash to a bech32m address")
@click.argument("puzzle_hash", nargs=1, required=True)
@click.option("-p", "--prefix", type=str, default="xch", show_default=True, required=False)
def encode_cmd(puzzle_hash, prefix):
    print(encode_puzzle_hash(bytes.fromhex(puzzle_hash), prefix))

@cli.command("decode", short_help="Decode a bech32m address to a puzzle hash")
@click.argument("address", nargs=1, required=True)
def encode_cmd(address):
    print(decode_puzzle_hash(address).hex())

cli.add_command(clsp.clsp_cmd)

def main() -> None:
    monkey_patch_click()
    cli()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()