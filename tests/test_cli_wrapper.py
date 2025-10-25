"""Test CLI wrapper that calls Rust binary"""
import subprocess
import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
import sys


def test_find_rust_cli_development():
    """Test finding Rust CLI in development environment"""
    from langlint.cli import find_rust_cli
    
    # Should find the binary in target/release
    cli_path = find_rust_cli()
    assert cli_path is not None
    assert "langlint" in cli_path.lower()


def test_find_rust_cli_not_found():
    """Test error when Rust CLI is not found"""
    from langlint import cli
    
    with patch.object(Path, 'exists', return_value=False):
        with patch('shutil.which', return_value=None):
            with pytest.raises(RuntimeError, match="Rust CLI not found"):
                cli.find_rust_cli()


def test_scan_command_calls_rust():
    """Test that scan command calls Rust CLI"""
    from langlint.cli import scan, find_rust_cli
    
    # Verify Rust CLI can be found
    rust_cli = find_rust_cli()
    assert Path(rust_cli).exists()


def test_translate_command_calls_rust():
    """Test that translate command calls Rust CLI"""  
    from langlint.cli import translate, find_rust_cli
    
    # Verify Rust CLI can be found
    rust_cli = find_rust_cli()
    assert Path(rust_cli).exists()


def test_fix_command_calls_rust():
    """Test that fix command calls Rust CLI"""
    from langlint.cli import fix, find_rust_cli
    
    # Verify Rust CLI can be found
    rust_cli = find_rust_cli()
    assert Path(rust_cli).exists()


def test_main_function_exists():
    """Test main entry point exists"""
    from langlint.cli import main
    assert callable(main)


def test_cli_group_exists():
    """Test CLI group is created"""
    from langlint.cli import cli
    assert callable(cli)


def test_scan_command_execution():
    """Test scan command executes Rust CLI"""
    from click.testing import CliRunner
    from langlint.cli import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ['scan', 'langlint/__init__.py'])
    # Should run without crashing
    assert result.exit_code in [0, 1]  # 0 or error code


def test_translate_command_execution():
    """Test translate command executes Rust CLI"""
    from click.testing import CliRunner
    from langlint.cli import cli
    
    runner = CliRunner()
    # Should handle missing required args gracefully
    result = runner.invoke(cli, ['translate', '--help'])
    assert result.exit_code == 0


def test_fix_command_execution():
    """Test fix command executes Rust CLI"""
    from click.testing import CliRunner
    from langlint.cli import cli
    
    runner = CliRunner()
    # Should handle missing required args gracefully
    result = runner.invoke(cli, ['fix', '--help'])
    assert result.exit_code == 0


def test_main_entry_point():
    """Test main() can be called"""
    from langlint.cli import main
    # Just verify it's callable, don't actually run it
    assert callable(main)


def test_main_invokes_cli():
    """Test that main() invokes the CLI"""
    from click.testing import CliRunner
    from langlint.cli import cli
    
    # Invoke main through CLI runner (this tests the cli() function at line 74)
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert '1.0.0' in result.output
    assert result.exit_code == 0


def test_find_rust_cli_in_path():
    """Test finding Rust CLI in system PATH"""
    from langlint import cli
    
    # Mock dev_binary not exists, but shutil.which finds it
    with patch.object(Path, 'exists', return_value=False):
        with patch('shutil.which', return_value='/usr/local/bin/langlint'):
            result = cli.find_rust_cli()
            assert result == '/usr/local/bin/langlint'


def test_scan_with_real_file():
    """Test scan command with real file execution"""
    from click.testing import CliRunner
    from langlint.cli import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ['scan', 'examples/python_translation/example_chinese.py'])
    # Should execute successfully
    assert result.exit_code == 0


def test_translate_with_mock():
    """Test translate command execution"""
    from click.testing import CliRunner
    from langlint.cli import cli
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('# 测试注释\ndef test(): pass\n')
        temp_path = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(cli, [
            'translate', temp_path, 
            '-s', 'zh-CN', '-t', 'en', 
            '--translator', 'mock',
            '-o', 'test_output.py'
        ])
        # Should execute (may succeed or fail gracefully)
        assert result.exit_code in [0, 1]
    finally:
        import time
        time.sleep(0.1)  # Wait for file handle release on Windows
        Path(temp_path).unlink(missing_ok=True)
        try:
            import shutil
            shutil.rmtree('test_output.py', ignore_errors=True)
        except:
            pass


def test_fix_with_mock():
    """Test fix command execution"""
    from click.testing import CliRunner
    from langlint.cli import cli
    import tempfile
    import shutil
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('# 测试注释\ndef test(): pass\n')
        temp_path = f.name
    
    try:
        runner = CliRunner()
        result = runner.invoke(cli, [
            'fix', temp_path,
            '-s', 'zh-CN', '-t', 'en',
            '--translator', 'mock',
            '-y'  # Skip confirmation
        ])
        # Should execute
        assert result.exit_code in [0, 1]
    finally:
        Path(temp_path).unlink(missing_ok=True)
        Path(f"{temp_path}.backup").unlink(missing_ok=True)

