"""Advanced CLI tests for full coverage"""
import pytest
import subprocess
import json
from pathlib import Path


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file"""
    file = tmp_path / "test.py"
    file.write_text('"""Hello"""')
    return str(file)


def test_cli_scan_with_format_text(sample_file):
    """Test scan command with text format"""
    result = subprocess.run(
        ["langlint", "scan", sample_file, "--format", "text"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_cli_scan_with_verbose(sample_file):
    """Test scan command with verbose flag"""
    result = subprocess.run(
        ["langlint", "scan", sample_file, "-v"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_cli_translate_with_dry_run(sample_file):
    """Test translate with dry run"""
    result = subprocess.run(
        ["langlint", "translate", sample_file, 
         "--source", "en", "--target", "zh", 
         "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    assert result.returncode == 0
    assert "Dry run" in result.stdout or "dry run" in result.stdout.lower()


def test_cli_translate_with_output(sample_file, tmp_path):
    """Test translate with output option"""
    output = str(tmp_path / "output.py")
    result = subprocess.run(
        ["langlint", "translate", sample_file,
         "--source", "en", "--target", "zh",
         "--output", output],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert Path(output).exists()


def test_cli_translate_google_translator(sample_file, tmp_path):
    """Test translate with Google translator"""
    output = str(tmp_path / "google_output.py")
    result = subprocess.run(
        ["langlint", "translate", sample_file,
         "--source", "en", "--target", "zh",
         "--translator", "google",
         "--output", output],
        capture_output=True,
        text=True
    )
    # May succeed or fail depending on network
    assert result.returncode in [0, 1]


def test_cli_fix_with_yes(sample_file):
    """Test fix command with --yes flag"""
    result = subprocess.run(
        ["langlint", "fix", sample_file,
         "--source", "en", "--target", "zh",
         "--yes"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    assert result.returncode == 0
    assert "fixed" in result.stdout.lower() or "translated" in result.stdout.lower()


def test_cli_fix_with_translator(sample_file):
    """Test fix command with custom translator"""
    result = subprocess.run(
        ["langlint", "fix", sample_file,
         "--source", "en", "--target", "zh",
         "--translator", "mock",
         "--yes"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_cli_translate_error_handling():
    """Test translate error handling with invalid input"""
    result = subprocess.run(
        ["langlint", "translate", "nonexistent_file.py",
         "--source", "en", "--target", "zh"],
        capture_output=True,
        text=True
    )
    # Should fail with non-zero exit code
    assert result.returncode != 0


def test_cli_main_entry_point():
    """Test main() entry point"""
    from langlint.cli import main
    import sys
    
    # Save original argv
    original_argv = sys.argv
    
    try:
        # Test --version
        sys.argv = ["langlint", "--version"]
        try:
            main()
        except SystemExit as e:
            # Click exits with 0 for --version
            assert e.code == 0
    finally:
        # Restore argv
        sys.argv = original_argv


def test_cli_scan_short_options(sample_file):
    """Test scan with short option flags"""
    result = subprocess.run(
        ["langlint", "scan", sample_file, "-f", "json", "-v"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_cli_translate_short_options(sample_file, tmp_path):
    """Test translate with short option flags"""
    output = str(tmp_path / "out.py")
    result = subprocess.run(
        ["langlint", "translate", sample_file,
         "-s", "en", "-t", "zh", "-o", output],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_cli_fix_short_options(sample_file):
    """Test fix with short option flags"""
    result = subprocess.run(
        ["langlint", "fix", sample_file,
         "-s", "en", "-t", "zh", "-y"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

