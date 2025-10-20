"""
Translation modules for different translation services.

This package contains translators for various translation APIs including
OpenAI, DeepL, Google Translate, and Azure Translator.
"""

from .base import Translator, TranslationResult, TranslationError
from .openai_translator import OpenAITranslator
from .deepl_translator import DeepLTranslator
from .google_translator import GoogleTranslator
from .mock_translator import MockTranslator

__all__ = [
    "Translator",
    "TranslationResult",
    "TranslationError",
    "OpenAITranslator",
    "DeepLTranslator",
    "GoogleTranslator",
    "MockTranslator",
]
