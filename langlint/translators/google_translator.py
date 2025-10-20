"""
Google Translate translator for using Google's translation service.

This translator uses Google's free translation API to provide translations
with support for over 100 languages.
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from deep_translator import GoogleTranslator as GoogleTranslatorClient
    # 支持的语言列表
    LANGUAGES = {
        'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian',
        'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian',
        'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)',
        'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish',
        'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish',
        'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian', 'de': 'german', 'el': 'greek',
        'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 'haw': 'hawaiian', 'iw': 'hebrew', 'he': 'hebrew',
        'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian',
        'ga': 'irish', 'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh',
        'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao', 'la': 'latin',
        'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian', 'mg': 'malagasy',
        'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 'mn': 'mongolian',
        'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian', 'or': 'odia', 'ps': 'pashto', 'fa': 'persian',
        'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan',
        'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala',
        'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili',
        'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish',
        'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh',
        'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'
    }
except ImportError:
    GoogleTranslatorClient = None
    LANGUAGES = {}

from .base import Translator, TranslationResult, TranslationStatus, TranslationError


@dataclass
class GoogleConfig:
    """Configuration for Google translator."""
    service_urls: Optional[List[str]] = None
    timeout: int = 30
    retry_count: int = 3
    delay_range: tuple[float, float] = (0.3, 0.6)  # Random delay between requests (Google limits: 5 req/sec)


class GoogleTranslator(Translator):
    """
    Translator using Google's free translation service.

    This translator provides translations using Google's free translation API
    with support for over 100 languages.
    """

    def __init__(self, config: Optional[GoogleConfig] = None):
        """
        Initialize the Google translator.

        Args:
            config: Google configuration
        """
        if GoogleTranslatorClient is None:
            raise ImportError("deep-translator is required for Google translation. Install with: pip install deep-translator")

        self.config = config or GoogleConfig()

    @property
    def name(self) -> str:
        """Return the name of this translator."""
        return "Google Translate"

    @property
    def supported_languages(self) -> List[str]:
        """Return a list of supported language codes."""
        return list(LANGUAGES.keys())

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

        # Add random delay to avoid rate limiting
        delay = random.uniform(*self.config.delay_range)
        await asyncio.sleep(delay)

        try:
            # Perform translation using deep-translator
            translator = GoogleTranslatorClient(source=source_lang, target=target_lang)
            translated_text = translator.translate(text)

            # Calculate confidence score (deep-translator doesn't provide confidence)
            confidence_score = 0.9  # Default confidence for Google Translate

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                status=TranslationStatus.SUCCESS,
                confidence=confidence_score,
                metadata={
                    'detected_language': source_lang,  # deep-translator doesn't detect language
                    'original_confidence': confidence_score,
                    'translator': 'Google Translate (deep-translator)',
                    'service_urls': self.config.service_urls,
                    'timeout': self.config.timeout
                }
            )

        except Exception as e:
            raise TranslationError(
                f"Google translation failed: {str(e)}",
                translator_name="Google Translate",
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

        # Create concurrent translation tasks with semaphore to limit concurrency
        # Limit to 3 concurrent requests per batch to avoid rate limiting
        semaphore = asyncio.Semaphore(3)

        async def translate_single(text: str, index: int) -> TranslationResult:
            async with semaphore:
                try:
                    # Add random delay to respect Google's rate limit (5 req/sec)
                    await asyncio.sleep(random.uniform(*self.config.delay_range))

                    # Translate text using deep-translator
                    translator = GoogleTranslatorClient(source=source_lang, target=target_lang)
                    translated_text = await asyncio.to_thread(translator.translate, text)

                    # Handle empty translation results
                    if not translated_text or not translated_text.strip():
                        translated_text = text  # Fallback to original text

                    return TranslationResult(
                        original_text=text,
                        translated_text=translated_text,
                        source_language=source_lang,
                        target_language=target_lang,
                        status=TranslationStatus.SUCCESS,
                        confidence=0.9,
                        metadata={
                            'detected_language': source_lang,
                            'original_confidence': 0.9,
                            'translator': 'Google Translate (deep-translator)',
                            'batch_index': index,
                            'service_urls': self.config.service_urls,
                            'timeout': self.config.timeout
                        }
                    )

                except Exception as e:
                    # On error, return original text to avoid breaking the pipeline
                    return TranslationResult(
                        original_text=text,
                        translated_text=text,  # Use original text as fallback
                        source_language=source_lang,
                        target_language=target_lang,
                        status=TranslationStatus.FAILED,
                        confidence=0.0,
                        metadata={
                            'error': str(e),
                            'batch_index': index,
                            'translator': 'Google Translate (deep-translator)'
                        }
                    )

        # Execute all translations concurrently with semaphore control
        tasks = [translate_single(text, i) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)

        return list(results)

    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language code is supported by this translator.

        Args:
            language_code: Language code to check

        Returns:
            True if the language is supported, False otherwise
        """
        normalized = self.normalize_language_code(language_code)
        # Check both the normalized code and the original code
        return normalized in LANGUAGES or language_code.lower() in LANGUAGES

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

        # Warn if using 'zh' without region specifier
        if normalized == 'zh':
            import warnings
            warnings.warn(
                "Language code 'zh' is ambiguous. Please use 'zh-CN' for Simplified Chinese "
                "or 'zh-TW' for Traditional Chinese. Defaulting to 'zh-CN'.",
                UserWarning
            )

        # Handle common variations - deep-translator uses specific codes
        variations = {
            'en-us': 'en',
            'en-gb': 'en',
            'zh': 'zh-CN',  # Default Chinese to Simplified
            'zh-cn': 'zh-CN',
            'zh-tw': 'zh-TW',
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
            Estimated cost (always 0 for Google Translate free tier)
        """
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
            'cost_per_character': 0.0,  # Free
            'max_batch_size': 100,  # Reasonable batch size
            'rate_limit': 'No official limit, but delays added to avoid blocking',
            'service_urls': self.config.service_urls,
            'timeout': self.config.timeout,
            'retry_count': self.config.retry_count,
            'delay_range': self.config.delay_range,
        }

    def _calculate_confidence(self, confidence: float, result: Any) -> float:
        """
        Calculate confidence score based on the Google Translate result.

        Args:
            confidence: Confidence from Google Translate
            result: Google Translate result object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Google Translate confidence is typically between 0 and 1
        if confidence is None:
            return 0.8  # Default confidence

        # Normalize confidence to 0-1 range
        normalized_confidence = max(0.0, min(1.0, confidence))

        # Adjust based on result quality indicators
        if hasattr(result, 'text') and result.text:
            # Check if translation looks reasonable
            if len(result.text.strip()) > 0:
                return normalized_confidence
            else:
                return 0.1  # Very low confidence for empty results

        return normalized_confidence

    def get_language_name(self, language_code: str) -> str:
        """
        Get the full language name for a language code.

        Args:
            language_code: Language code

        Returns:
            Full language name
        """
        normalized = self.normalize_language_code(language_code)
        return LANGUAGES.get(normalized, language_code)

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
