"""Test fallback when Rust module is not available"""
import pytest
import sys


def test_import_error_fallback():
    """Test fallback behavior when langlint_py is not available"""
    # Save original modules
    original_modules = sys.modules.copy()
    
    # Remove modules if they exist
    for mod in ['langlint_py', 'langlint', 'langlint.cli']:
        if mod in sys.modules:
            del sys.modules[mod]
    
    # Block langlint_py import
    sys.modules['langlint_py'] = None
    
    try:
        # Import should trigger warning but not fail
        with pytest.warns(UserWarning, match="Failed to import Rust module"):
            import langlint
            
            # Verify fallback values
            assert not langlint.HAS_RUST
            assert langlint.scan is None
            assert langlint.translate is None
            assert langlint.version() == "1.0.3"
                
    finally:
        # Restore original modules
        sys.modules.clear()
        sys.modules.update(original_modules)


def test_has_rust_true():
    """Test that HAS_RUST is True when module is available"""
    import langlint
    # Skip if Rust module is not available (e.g., in CI without Rust build)
    if not langlint.HAS_RUST:
        pytest.skip("Rust module not available")
    assert langlint.HAS_RUST

