"""
Command-line interface for LangLint (Rust-powered).

This is a thin Python wrapper that calls the Rust CLI binary.
All actual processing is done by the Rust CLI (target/release/langlint).
"""

import sys
import subprocess
import shutil
from pathlib import Path
import click

try:
    from importlib.metadata import version as _pkg_version
except ImportError:
    _pkg_version = None


def _cli_version() -> str:
    if _pkg_version is None:
        return "unknown"
    try:
        return _pkg_version("langlint")
    except Exception:
        return "unknown"


def _rust_cli_filename() -> str:
    return "langlint.exe" if sys.platform.startswith("win") else "langlint"


def find_rust_cli():
    """Find the Rust CLI binary."""
    package_binary = Path(__file__).parent / _rust_cli_filename()
    if package_binary.exists():
        return str(package_binary)

    site_root_binary = Path(__file__).resolve().parent.parent / _rust_cli_filename()
    if site_root_binary.exists():
        return str(site_root_binary)
    
    repo_root = Path(__file__).parent.parent
    dev_binary = repo_root / "target" / "release" / _rust_cli_filename()
    if dev_binary.exists():
        return str(dev_binary)
    
    current_entry = None
    try:
        current_entry = Path(sys.argv[0]).resolve()
    except Exception:
        current_entry = None

    for candidate in ("langlint.exe", "langlint"):
        cli_path = shutil.which(candidate)
        if not cli_path:
            continue

        try:
            resolved = Path(cli_path).resolve()
        except Exception:
            resolved = None

        if current_entry is not None and resolved is not None and resolved == current_entry:
            continue

        if candidate == "langlint" and not str(cli_path).lower().endswith(".exe"):
            continue

        return cli_path
    
    raise RuntimeError(
        "Rust CLI not found. Please build it first:\n"
        "  cargo build --release -p langlint_cli"
    )


@click.group()
@click.version_option(version=_cli_version(), prog_name="langlint")
def cli():
    """
    LangLint: High-performance, Rust-powered translation toolkit.
    
    Breaking language barriers in global collaboration with 10-50x speedup!
    """
    pass


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def scan(args):
    """Scan files and extract translatable units."""
    rust_cli = find_rust_cli()
    result = subprocess.run([rust_cli, 'scan'] + list(args))
    sys.exit(result.returncode)


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def translate(args):
    """Translate files to a new location."""
    rust_cli = find_rust_cli()
    result = subprocess.run([rust_cli, 'translate'] + list(args))
    sys.exit(result.returncode)


@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def fix(args):
    """Fix (in-place translate) files with automatic backup."""
    rust_cli = find_rust_cli()
    result = subprocess.run([rust_cli, 'fix'] + list(args))
    sys.exit(result.returncode)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
