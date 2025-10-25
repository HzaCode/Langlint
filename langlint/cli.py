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


def find_rust_cli():
    """Find the Rust CLI binary."""
    # Check in target/release first (development)
    repo_root = Path(__file__).parent.parent
    dev_binary = repo_root / "target" / "release" / "langlint.exe"
    if dev_binary.exists():
        return str(dev_binary)
    
    # Check if it's in PATH (installed)
    cli_path = shutil.which("langlint")
    if cli_path:
        return cli_path
    
    raise RuntimeError(
        "Rust CLI not found. Please build it first:\n"
        "  cargo build --release -p langlint_cli"
    )


@click.group()
@click.version_option(version="1.0.0", prog_name="langlint")
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
