"""Test fallback behavior when Rust module is not available"""
import pytest
import sys
import importlib


def test_fallback_import_error():
    """Test fallback when langlint_py is not available"""
    # Temporarily block langlint_py import
    original_modules = sys.modules.copy()
    
    # Remove langlint_py if it exists
    if 'langlint_py' in sys.modules:
        del sys.modules['langlint_py']
    if 'langlint' in sys.modules:
        del sys.modules['langlint']
    
    # Block langlint_py import
    sys.modules['langlint_py'] = None
    
    try:
        # Import should trigger fallback warning
        with pytest.warns(UserWarning, match="Failed to import Rust module"):
            import langlint
            importlib.reload(langlint)
            
            # Test fallback version function
            assert langlint.version() == "1.0.0"
            
            # Test fallback scan raises error
            with pytest.raises(RuntimeError, match="Rust module not built"):
                langlint.scan("test.py")
            
            # Test fallback translate raises error
            with pytest.raises(RuntimeError, match="Rust module not built"):
                langlint.translate("test.py", "en", "zh")
                
    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


def test_rust_module_available():
    """Test that Rust module is actually available in our environment"""
    try:
        from langlint_py import scan, translate, version
        assert scan is not None
        assert translate is not None
        assert version is not None
        assert version() == "1.0.0"
    except ImportError:
        pytest.skip("Rust module not available")

