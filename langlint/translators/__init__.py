"""
Translation modules for different translation services.

This package contains translators for Google Translate and mock testing.
"""

from .base import Translator, TranslationResult, TranslationError
from .google_translator import GoogleTranslator
from .mock_translator import MockTranslator

__all__ = [
    "Translator",
    "TranslationResult",
    "TranslationError",
    "GoogleTranslator",
    "MockTranslator",
]
