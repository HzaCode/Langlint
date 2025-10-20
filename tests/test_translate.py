"""Test translation functionality"""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing"""
    file_path = tmp_path / "test_translate.py"
    file_path.write_text('''
"""Hello World"""

def greet():
    """Say hello"""
    # This is a comment
    return "Hello"
''')
    return str(file_path)


def test_translate_basic(sample_python_file, tmp_path):
    """Test basic translation functionality"""
    try:
        from langlint_py import translate
    except ImportError:
        pytest.skip("Rust module not built")
    
    output_path = str(tmp_path / "translated.py")
    result = translate(
        sample_python_file,
        "en",
        "zh",
        translator="mock",
        output=output_path,
        dry_run=False
    )
    
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["translated"] > 0
    assert Path(output_path).exists()


def test_translate_dry_run(sample_python_file, tmp_path):
    """Test translation with dry run"""
    try:
        from langlint_py import translate
    except ImportError:
        pytest.skip("Rust module not built")
    
    output_path = str(tmp_path / "translated_dry.py")
    result = translate(
        sample_python_file,
        "en",
        "zh",
        translator="mock",
        output=output_path,
        dry_run=True
    )
    
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["dry_run"] is True
    assert not Path(output_path).exists()  # Should not create file in dry run


def test_translate_mock_translator(sample_python_file, tmp_path):
    """Test translation with mock translator"""
    try:
        from langlint_py import translate
    except ImportError:
        pytest.skip("Rust module not built")
    
    output_path = str(tmp_path / "translated_mock.py")
    result = translate(
        sample_python_file,
        "en",
        "zh",
        translator="mock"
    )
    
    data = json.loads(result)
    assert data["status"] == "success"


def test_translate_invalid_file():
    """Test translation with invalid file"""
    try:
        from langlint_py import translate
    except ImportError:
        pytest.skip("Rust module not built")
    
    with pytest.raises(Exception):
        translate(
            "nonexistent.py",
            "en",
            "zh",
            translator="mock"
        )

