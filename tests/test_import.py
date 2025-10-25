"""Test basic imports and version"""
import pytest


def test_import_langlint():
    """Test that langlint can be imported"""
    import langlint
    assert langlint is not None


def test_version():
    """Test that version is correctly set"""
    import langlint
    assert langlint.__version__ == "1.0.1"


def test_import_rust_module():
    """Test that Rust module can be imported"""
    try:
        from langlint_py import scan, translate, version
        assert scan is not None
        assert translate is not None
        assert version is not None
        assert version() == "1.0.1"
    except ImportError:
        pytest.skip("Rust module not built")

