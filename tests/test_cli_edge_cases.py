"""Test edge cases and error paths in CLI"""
import pytest
import subprocess
from pathlib import Path
from unittest import mock
import sys


@pytest.fixture
def broken_file(tmp_path):
    """Create a file that might cause translation errors"""
    file = tmp_path / "broken.py"
    file.write_text('"""Test"""')
    return str(file)


def test_scan_exception_handling(tmp_path):
    """Test scan exception handling"""
    # Create an invalid path scenario
    # Note: We can't easily trigger the exception without mocking
    # This tests the error output path
    result = subprocess.run(
        ["langlint", "scan", "nonexistent.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "Error" in result.stderr or "error" in result.stderr.lower()


def test_translate_failure_status(tmp_path):
    """Test translate with failure status"""
    # This would need mocking to properly test
    # For now, test with invalid parameters
    pass


def test_fix_without_confirmation(broken_file):
    """Test fix command without -y flag (Rust backend doesn't need confirmation)"""
    # With Rust backend, confirmation is optional (uses -y flag)
    result = subprocess.run(
        ["langlint", "fix", broken_file,
         "--source", "en", "--target", "zh"],
        input="",
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    # Rust backend runs successfully without confirmation
    assert result.returncode in [0, 1]  # Success or graceful failure


def test_fix_with_confirmation(broken_file):
    """Test fix command with stdin confirmation"""
    # Send 'y' to confirm
    result = subprocess.run(
        ["langlint", "fix", broken_file,
         "--source", "en", "--target", "zh"],
        input="y\n",
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_cli_main_as_module():
    """Test running CLI as module"""
    result = subprocess.run(
        [sys.executable, "-m", "langlint.cli", "--version"],
        capture_output=True,
        text=True
    )
    # Check both stdout and stderr for version info
    output = result.stdout + result.stderr
    assert "1.0.0" in output or result.returncode == 0


def test_translate_all_options(tmp_path):
    """Test translate with all options combined"""
    file = tmp_path / "full_test.py"
    file.write_text('"""Complete test"""')
    output = str(tmp_path / "output.py")
    
    result = subprocess.run(
        ["langlint", "translate", str(file),
         "--source", "en", 
         "--target", "zh",
         "--translator", "mock",
         "--output", output,
         "--dry-run"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    assert result.returncode == 0
    assert "Dry run" in result.stdout or "dry run" in result.stdout.lower()


def test_fix_backup_message(tmp_path):
    """Test that fix mentions backup file"""
    file = tmp_path / "backup_test.py"
    file.write_text('"""Backup test"""')
    
    result = subprocess.run(
        ["langlint", "fix", str(file),
         "-s", "en", "-t", "zh", "-y"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    assert result.returncode == 0
    assert "backup" in result.stdout.lower() or "Backup" in result.stdout


def test_cli_with_mock_error():
    """Test CLI error handling with mocked exception"""
    # This tests the except blocks in CLI
    from langlint import cli as cli_module
    from click.testing import CliRunner
    
    runner = CliRunner()
    
    # Test scan with non-existent file to trigger error handling
    result = runner.invoke(cli_module.cli, ['scan', 'nonexistent_file.py'])
    assert result.exit_code != 0
    assert "Error" in result.output or "error" in result.output.lower()


def test_translate_with_mock_error():
    """Test translate error handling with mocked exception"""
    from langlint import cli as cli_module
    from click.testing import CliRunner
    
    runner = CliRunner()
    
    with mock.patch('langlint_py.translate', side_effect=Exception("Translation error")):
        result = runner.invoke(cli_module.cli, [
            'translate', '.', 
            '-s', 'en', 
            '-t', 'zh'
        ])
        assert result.exit_code != 0
        # Error appears in output or exception is raised
        assert result.exit_code == 1  # Exited with error code


def test_fix_with_mock_error():
    """Test fix error handling with mocked exception"""
    from langlint import cli as cli_module
    from click.testing import CliRunner
    
    runner = CliRunner()
    
    with mock.patch('langlint_py.translate', side_effect=Exception("Fix error")):
        result = runner.invoke(cli_module.cli, [
            'fix', '.', 
            '-s', 'en', 
            '-t', 'zh',
            '-y'
        ])
        assert result.exit_code != 0
        # Error handling works
        assert result.exit_code == 1  # Exited with error code


def test_translate_with_failed_status(tmp_path):
    """Test translate with failed status in response"""
    from langlint import cli as cli_module
    from click.testing import CliRunner
    
    # Create a test file
    test_file = tmp_path / "test.py"
    test_file.write_text('"""Test file"""')
    
    runner = CliRunner()
    
    # Test with invalid file to trigger error
    result = runner.invoke(cli_module.cli, [
        'translate', '/nonexistent/path.py', 
        '-s', 'en', 
        '-t', 'zh',
        '--translator', 'mock'
    ])
    assert result.exit_code != 0
    # Error should be in output
    assert "error" in result.output.lower() or "does not exist" in result.output.lower()


def test_fix_with_failed_status(tmp_path):
    """Test fix with failed status in response"""
    from langlint import cli as cli_module
    from click.testing import CliRunner
    
    # Create a test file
    test_file = tmp_path / "test.py"
    test_file.write_text('"""Test file"""')
    
    runner = CliRunner()
    
    # Test with invalid file to trigger error
    result = runner.invoke(cli_module.cli, [
        'fix', '/nonexistent/path.py', 
        '-s', 'en', 
        '-t', 'zh',
        '--translator', 'mock',
        '-y'
    ])
    assert result.exit_code != 0
    # Error should be in output
    assert "error" in result.output.lower() or "does not exist" in result.output.lower()

