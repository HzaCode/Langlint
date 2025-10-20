"""Test CLI functionality"""
import subprocess
import json
import tempfile
import os


def test_cli_version():
    """Test CLI version command"""
    result = subprocess.run(["langlint", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "1.0.0" in result.stdout


def test_cli_help():
    """Test CLI help command"""
    result = subprocess.run(["langlint", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "scan" in result.stdout
    assert "translate" in result.stdout
    assert "fix" in result.stdout


def test_cli_scan():
    """Test CLI scan command"""
    result = subprocess.run(
        ["langlint", "scan", "demo_files/math_utils.py"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "files_scanned" in result.stdout or "units" in result.stdout.lower()


def test_cli_scan_nonexistent():
    """Test CLI scan with nonexistent file"""
    result = subprocess.run(
        ["langlint", "scan", "nonexistent_file.py"], capture_output=True, text=True
    )
    assert result.returncode != 0


def test_cli_scan_with_exclude():
    """Test CLI scan with exclude patterns"""
    result = subprocess.run(
        ["langlint", "scan", ".", "-e", "demo_files", "-e", "examples", "-f", "json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    
    # Verify demo_files and examples are excluded
    for item in data.get("results", []):
        file_path = item.get("file", "")
        assert "demo_files" not in file_path
        assert "examples" not in file_path


def test_cli_scan_output_includes_file_paths():
    """Test that scan JSON output includes file paths not just indices"""
    result = subprocess.run(
        ["langlint", "scan", "langlint/cli.py", "-f", "json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    
    # Verify results have "file" field not "file_index"
    assert "results" in data
    if len(data["results"]) > 0:
        first_result = data["results"][0]
        assert "file" in first_result
        assert "file_index" not in first_result
        # Verify it's a valid path
        assert "cli.py" in first_result["file"]


def test_cli_scan_with_output_file():
    """Test CLI scan with output file option"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        output_file = f.name
    
    try:
        result = subprocess.run(
            ["langlint", "scan", "langlint/__init__.py", "-f", "json", "-o", output_file],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Results written to" in result.stdout
        
        # Verify file was created and contains valid JSON
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert "files_scanned" in data
            assert "total_units" in data
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


def test_default_excludes_demo_files():
    """Test that demo_files is excluded by default"""
    result = subprocess.run(
        ["langlint", "scan", ".", "-f", "json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    
    # Verify demo_files, examples, figures are not in results
    for item in data.get("results", []):
        file_path = item.get("file", "")
        assert "demo_files" not in file_path
        assert "examples" not in file_path
        assert "figures" not in file_path
        assert "submission_patterns" not in file_path
