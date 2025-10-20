"""
Base translator classes and interfaces.

This module defines the abstract base classes that all translators must implement
to ensure a consistent interface across different translation services.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class TranslationStatus(Enum):
    """Status of a translation operation."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class TranslationResult:
    """
    Result of a translation operation.

    Attributes:
        original_text: The original text that was translated
        translated_text: The translated text
        source_language: Source language code
        target_language: Target language code
        status: Status of the translation
        confidence: Confidence score (0.0 to 1.0)
        metadata: Additional metadata about the translation
    """
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    status: TranslationStatus
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate the translation result after initialization."""
        if not self.original_text.strip():
            raise ValueError("Original text cannot be empty")
        if not self.translated_text.strip():
            raise ValueError("Translated text cannot be empty")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")


class Translator(ABC):
    """
    Abstract base class for all translation services.

    All translators must implement the methods defined in this class to ensure
    a consistent interface across different translation services.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of this translator.

        Returns:
            Translator name
        """
        pass

    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """
        Return a list of supported language codes.

        Returns:
            List of supported language codes (e.g., ['en', 'zh', 'ja', 'ko'])
        """
        pass

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        **kwargs: Any
    ) -> TranslationResult:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code
            **kwargs: Additional translator-specific parameters

        Returns:
            TranslationResult containing the translated text and metadata

        Raises:
            TranslationError: If translation fails
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        **kwargs: Any
    ) -> List[TranslationResult]:
        """
        Translate multiple texts in a single batch operation.

        Args:
            texts: List of texts to translate
            source_language: Source language code
            target_language: Target language code
            **kwargs: Additional translator-specific parameters

        Returns:
            List of TranslationResult objects

        Raises:
            TranslationError: If batch translation fails
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language code is supported by this translator.

        Args:
            language_code: Language code to check

        Returns:
            True if the language is supported, False otherwise
        """
        pass

    def validate_languages(self, source_language: str, target_language: str) -> None:
        """
        Validate that both source and target languages are supported.

        Args:
            source_language: Source language code
            target_language: Target language code

        Raises:
            ValueError: If either language is not supported
        """
        if not self.is_language_supported(source_language):
            raise ValueError(f"Source language '{source_language}' is not supported by {self.name}")

        if not self.is_language_supported(target_language):
            raise ValueError(f"Target language '{target_language}' is not supported by {self.name}")

    def normalize_language_code(self, language_code: str) -> str:
        """
        Normalize a language code to the format expected by this translator.

        Args:
            language_code: Language code to normalize

        Returns:
            Normalized language code
        """
        # Default implementation returns the code as-is
        # Subclasses can override this to handle specific formats
        return language_code.lower()

    def get_supported_language_pairs(self) -> List[tuple[str, str]]:
        """
        Get all supported language pairs for this translator.

        Returns:
            List of (source, target) language code tuples
        """
        languages = self.supported_languages
        pairs = []
        for source in languages:
            for target in languages:
                if source != target:
                    pairs.append((source, target))
        return pairs

    def estimate_cost(self, text: str, source_language: str, target_language: str) -> float:
        """
        Estimate the cost of translating the given text.

        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code

        Returns:
            Estimated cost in the translator's currency
        """
        # Default implementation returns 0 (free)
        # Subclasses can override this to provide actual cost estimates
        return 0.0

    def get_usage_info(self) -> Dict[str, Any]:
        """
        Get usage information for this translator.

        Returns:
            Dictionary containing usage information
        """
        return {
            'name': self.name,
            'supported_languages': self.supported_languages,
            'supported_pairs': self.get_supported_language_pairs(),
            'cost_per_character': 0.0,  # Default to free
            'max_batch_size': 100,  # Default batch size
            'rate_limit': None,  # No rate limit by default
        }


class TranslationError(Exception):
    """Exception raised for translation-related errors."""

    def __init__(self, message: str, translator_name: str = "", error_code: str = ""):
        """
        Initialize a translation error.

        Args:
            message: Error message
            translator_name: Name of the translator that caused the error
            error_code: Error code from the translation service
        """
        super().__init__(message)
        self.translator_name = translator_name
        self.error_code = error_code

    def __str__(self) -> str:
        """Return a formatted error message."""
        parts = [super().__str__()]
        if self.translator_name:
            parts.append(f"Translator: {self.translator_name}")
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        return " | ".join(parts)
