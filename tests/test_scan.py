"""Test scan functionality"""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing"""
    file_path = tmp_path / "test.py"
    file_path.write_text('''
"""This is a module docstring"""

def hello():
    """This is a function docstring"""
    # This is a comment
    print("Hello, World!")
''')
    return str(file_path)


def test_scan_basic():
    """Test basic scan functionality"""
    try:
        from langlint_py import scan
    except ImportError:
        pytest.skip("Rust module not built")
    
    result = scan("demo_files/math_utils.py")
    data = json.loads(result)
    
    assert "files_scanned" in data
    assert "total_units" in data
    assert data["files_scanned"] == 1
    assert data["total_units"] > 0


def test_scan_with_sample_file(sample_python_file):
    """Test scan with a sample file"""
    try:
        from langlint_py import scan
    except ImportError:
        pytest.skip("Rust module not built")
    
    result = scan(sample_python_file)
    data = json.loads(result)
    
    assert data["files_scanned"] == 1
    assert data["total_units"] >= 2  # At least docstring and comment


def test_scan_nonexistent_file():
    """Test scan with nonexistent file"""
    try:
        from langlint_py import scan
    except ImportError:
        pytest.skip("Rust module not built")
    
    with pytest.raises(Exception):
        scan("nonexistent_file.py")

