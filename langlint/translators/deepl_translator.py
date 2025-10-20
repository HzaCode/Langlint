"""
DeepL translator for using DeepL API for translation.

This translator uses DeepL's translation API to provide high-quality translations
with support for many languages and specialized terminology.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    import deepl
    from deepl import Translator as DeepLTranslator
except ImportError:
    deepl = None
    DeepLTranslator = None

from .base import Translator, TranslationResult, TranslationStatus, TranslationError


@dataclass
class DeepLConfig:
    """Configuration for DeepL translator."""
    api_key: str
    base_url: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    formality: str = "default"  # default, more, less, prefer_more, prefer_less


class DeepLTranslator(Translator):
    """
    Translator using DeepL's translation API.

    This translator provides high-quality translations with support for many
    languages and specialized terminology using DeepL's translation service.
    """

    # Language code mapping for DeepL
    LANGUAGE_MAPPING = {
        'en': 'EN',
        'de': 'DE',
        'fr': 'FR',
        'it': 'IT',
        'ja': 'JA',
        'es': 'ES',
        'nl': 'NL',
        'pl': 'PL',
        'pt': 'PT',
        'ru': 'RU',
        'zh': 'ZH',
        'ko': 'KO',
        'ar': 'AR',
        'bg': 'BG',
        'cs': 'CS',
        'da': 'DA',
        'el': 'EL',
        'et': 'ET',
        'fi': 'FI',
        'hu': 'HU',
        'id': 'ID',
        'lt': 'LT',
        'lv': 'LV',
        'nb': 'NB',
        'ro': 'RO',
        'sk': 'SK',
        'sl': 'SL',
        'sv': 'SV',
        'tr': 'TR',
        'uk': 'UK',
    }

    def __init__(self, config: DeepLConfig):
        """
        Initialize the DeepL translator.

        Args:
            config: DeepL configuration
        """
        if deepl is None:
            raise ImportError("deepl is required for DeepL translation. Install with: pip install deepl")

        self.config = config
        self.client = DeepLTranslator(
            auth_key=config.api_key,
            server_url=config.base_url
        )

    @property
    def name(self) -> str:
        """Return the name of this translator."""
        return "DeepL"

    @property
    def supported_languages(self) -> List[str]:
        """Return a list of supported language codes."""
        return list(self.LANGUAGE_MAPPING.keys())

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
            **kwargs: Additional parameters

        Returns:
            TranslationResult containing the translated text and metadata

        Raises:
            TranslationError: If translation fails
        """
        # Validate languages
        self.validate_languages(source_language, target_language)

        # Normalize language codes
        source_lang = self.normalize_language_code(source_language)
        target_lang = self.normalize_language_code(target_language)

        # Get DeepL language codes
        source_deepl = self.LANGUAGE_MAPPING.get(source_lang)
        target_deepl = self.LANGUAGE_MAPPING.get(target_lang)

        if not source_deepl or not target_deepl:
            raise ValueError(f"Unsupported language pair: {source_lang} -> {target_lang}")

        # Get additional parameters
        formality = kwargs.get('formality', self.config.formality)

        try:
            # Call DeepL API
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.translate_text(
                    text,
                    source_lang=source_deepl,
                    target_lang=target_deepl,
                    formality=formality
                )
            )

            # Extract translated text
            translated_text = result.text

            # Calculate confidence (DeepL doesn't provide confidence scores)
            confidence = 0.95  # DeepL is generally very accurate

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                status=TranslationStatus.SUCCESS,
                confidence=confidence,
                metadata={
                    'formality': formality,
                    'detected_source_language': result.detected_source_lang,
                    'translator': 'DeepL'
                }
            )

        except Exception as e:
            raise TranslationError(
                f"DeepL translation failed: {str(e)}",
                translator_name="DeepL",
                error_code=getattr(e, 'code', 'UNKNOWN')
            ) from e

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
            **kwargs: Additional parameters

        Returns:
            List of TranslationResult objects
        """
        # Validate languages
        self.validate_languages(source_language, target_language)

        # Normalize language codes
        source_lang = self.normalize_language_code(source_language)
        target_lang = self.normalize_language_code(target_language)

        # Get DeepL language codes
        source_deepl = self.LANGUAGE_MAPPING.get(source_lang)
        target_deepl = self.LANGUAGE_MAPPING.get(target_lang)

        if not source_deepl or not target_deepl:
            raise ValueError(f"Unsupported language pair: {source_lang} -> {target_lang}")

        # Get additional parameters
        formality = kwargs.get('formality', self.config.formality)

        try:
            # Call DeepL API for batch translation
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.translate_text(
                    texts,
                    source_lang=source_deepl,
                    target_lang=target_deepl,
                    formality=formality
                )
            )

            # Create results
            translation_results = []
            for i, (original_text, result) in enumerate(zip(texts, results)):
                translation_results.append(TranslationResult(
                    original_text=original_text,
                    translated_text=result.text,
                    source_language=source_lang,
                    target_language=target_lang,
                    status=TranslationStatus.SUCCESS,
                    confidence=0.95,  # DeepL is generally very accurate
                    metadata={
                        'formality': formality,
                        'detected_source_language': result.detected_source_lang,
                        'batch_index': i,
                        'translator': 'DeepL'
                    }
                ))

            return translation_results

        except Exception as e:
            raise TranslationError(
                f"DeepL batch translation failed: {str(e)}",
                translator_name="DeepL",
                error_code=getattr(e, 'code', 'UNKNOWN')
            ) from e

    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language code is supported by this translator.

        Args:
            language_code: Language code to check

        Returns:
            True if the language is supported, False otherwise
        """
        normalized = self.normalize_language_code(language_code)
        return normalized in self.LANGUAGE_MAPPING

    def normalize_language_code(self, language_code: str) -> str:
        """
        Normalize a language code to the format expected by this translator.

        Args:
            language_code: Language code to normalize

        Returns:
            Normalized language code
        """
        # Convert to lowercase and handle common variations
        normalized = language_code.lower()

        # Handle common variations
        variations = {
            'en-us': 'en',
            'en-gb': 'en',
            'zh-cn': 'zh',
            'zh-tw': 'zh',
            'ja-jp': 'ja',
            'ko-kr': 'ko',
            'fr-fr': 'fr',
            'de-de': 'de',
            'es-es': 'es',
            'it-it': 'it',
            'pt-br': 'pt',
            'pt-pt': 'pt',
            'ru-ru': 'ru',
            'ar-sa': 'ar',
            'hi-in': 'hi',
            'th-th': 'th',
            'vi-vn': 'vi',
            'id-id': 'id',
            'ms-my': 'ms',
            'tl-ph': 'tl',
            'tr-tr': 'tr',
            'pl-pl': 'pl',
            'nl-nl': 'nl',
            'sv-se': 'sv',
            'da-dk': 'da',
            'no-no': 'no',
            'fi-fi': 'fi',
            'cs-cz': 'cs',
            'hu-hu': 'hu',
            'ro-ro': 'ro',
            'bg-bg': 'bg',
            'hr-hr': 'hr',
            'sk-sk': 'sk',
            'sl-si': 'sl',
            'et-ee': 'et',
            'lv-lv': 'lv',
            'lt-lt': 'lt',
            'uk-ua': 'uk',
            'be-by': 'be',
            'mk-mk': 'mk',
            'sq-al': 'sq',
            'sr-rs': 'sr',
            'bs-ba': 'bs',
            'me-me': 'me',
            'is-is': 'is',
            'ga-ie': 'ga',
            'cy-gb': 'cy',
            'mt-mt': 'mt',
            'eu-es': 'eu',
            'ca-es': 'ca',
            'gl-es': 'gl',
            'af-za': 'af',
            'sw-ke': 'sw',
            'am-et': 'am',
            'az-az': 'az',
            'bn-bd': 'bn',
            'gu-in': 'gu',
            'he-il': 'he',
            'ka-ge': 'ka',
            'kk-kz': 'kk',
            'ky-kg': 'ky',
            'lo-la': 'lo',
            'mn-mn': 'mn',
            'my-mm': 'my',
            'ne-np': 'ne',
            'si-lk': 'si',
            'ta-in': 'ta',
            'te-in': 'te',
            'ur-pk': 'ur',
            'uz-uz': 'uz',
        }

        return variations.get(normalized, normalized)

    def estimate_cost(self, text: str, source_language: str, target_language: str) -> float:
        """
        Estimate the cost of translating the given text.

        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code

        Returns:
            Estimated cost in USD
        """
        # DeepL pricing (as of 2024)
        # Free tier: 500,000 characters per month
        # Pro tier: $6.99/month for 500,000 characters, then $0.000025 per character

        char_count = len(text)

        # Assume Pro tier pricing
        cost_per_char = 0.000025

        return char_count * cost_per_char

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
            'cost_per_character': 0.000025,  # Pro tier pricing
            'max_batch_size': 50,  # DeepL batch limit
            'rate_limit': '500 requests per month (free tier)',
            'formality': self.config.formality,
            'max_retries': self.config.max_retries,
            'timeout': self.config.timeout,
        }
