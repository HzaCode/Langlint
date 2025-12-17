"""
LangLint: High-performance, Rust-powered translation toolkit.

All core functionality is implemented in Rust (langlint_py).
This Python package provides a CLI wrapper for ease of use.
"""

__version__ = "1.0.3"
__author__ = "Zhiang He"
__email__ = "ang@hezhiang.com"
__license__ = "MIT"

# Import Rust module
try:
    import langlint_py
    HAS_RUST = True
    
    # Expose Rust functions
    scan = langlint_py.scan
    translate = langlint_py.translate
    version = langlint_py.version
    
except ImportError as e:
    import warnings
    warnings.warn(
        f"Failed to import Rust module (langlint_py): {e}\n"
        "Please reinstall: pip install langlint",
        UserWarning
    )
    HAS_RUST = False
    scan = None
    translate = None
    
    def version():
        """Return version string"""
        return __version__

# Import CLI main function
from .cli import main

__all__ = [
    "scan",
    "translate",
    "version",
    "main",
    "HAS_RUST",
]
