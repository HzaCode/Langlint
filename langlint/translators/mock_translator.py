"""
Mock translator for testing and development.

This translator provides a simple mock implementation that can be used
for testing without making actual API calls to translation services.
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .base import Translator, TranslationResult, TranslationStatus, TranslationError


@dataclass
class MockConfig:
    """Configuration for Mock translator."""
    delay_range: tuple[float, float] = (0.1, 0.5)  # Random delay in seconds
    error_rate: float = 0.0  # Probability of errors (0.0 to 1.0)
    confidence_range: tuple[float, float] = (0.8, 1.0)  # Random confidence range


class MockTranslator(Translator):
    """
    Mock translator for testing and development.

    This translator provides a simple mock implementation that can be used
    for testing without making actual API calls to translation services.
    """

    # Mock language mappings
    LANGUAGE_MAPPING = {
        'en': 'English',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'ms': 'Malay',
        'tl': 'Filipino',
        'tr': 'Turkish',
        'pl': 'Polish',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'cs': 'Czech',
        'hu': 'Hungarian',
        'ro': 'Romanian',
        'bg': 'Bulgarian',
        'hr': 'Croatian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'et': 'Estonian',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'uk': 'Ukrainian',
        'be': 'Belarusian',
        'mk': 'Macedonian',
        'sq': 'Albanian',
        'sr': 'Serbian',
        'bs': 'Bosnian',
        'me': 'Montenegrin',
        'is': 'Icelandic',
        'ga': 'Irish',
        'cy': 'Welsh',
        'mt': 'Maltese',
        'eu': 'Basque',
        'ca': 'Catalan',
        'gl': 'Galician',
        'af': 'Afrikaans',
        'sw': 'Swahili',
        'am': 'Amharic',
        'az': 'Azerbaijani',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'he': 'Hebrew',
        'ka': 'Georgian',
        'kk': 'Kazakh',
        'ky': 'Kyrgyz',
        'lo': 'Lao',
        'mn': 'Mongolian',
        'my': 'Burmese',
        'ne': 'Nepali',
        'si': 'Sinhala',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ur': 'Urdu',
        'uz': 'Uzbek',
    }

    def __init__(self, config: Optional[MockConfig] = None):
        """
        Initialize the Mock translator.

        Args:
            config: Mock configuration
        """
        self.config = config or MockConfig()

    @property
    def name(self) -> str:
        """Return the name of this translator."""
        return "Mock"

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

        # Simulate API delay
        delay = random.uniform(*self.config.delay_range)
        await asyncio.sleep(delay)

        # Simulate errors
        if random.random() < self.config.error_rate:
            raise TranslationError(
                f"Mock translation failed (simulated error)",
                translator_name="Mock",
                error_code="MOCK_ERROR"
            )

        # Generate mock translation
        translated_text = self._generate_mock_translation(text, source_lang, target_lang)

        # Generate confidence score
        confidence = random.uniform(*self.config.confidence_range)

        return TranslationResult(
            original_text=text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang,
            status=TranslationStatus.SUCCESS,
            confidence=confidence,
            metadata={
                'mock': True,
                'delay': delay,
                'translator': 'Mock'
            }
        )

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

        # Simulate API delay
        delay = random.uniform(*self.config.delay_range)
        await asyncio.sleep(delay)

        # Simulate errors
        if random.random() < self.config.error_rate:
            raise TranslationError(
                f"Mock batch translation failed (simulated error)",
                translator_name="Mock",
                error_code="MOCK_BATCH_ERROR"
            )

        # Generate mock translations
        results = []
        for i, text in enumerate(texts):
            translated_text = self._generate_mock_translation(text, source_lang, target_lang)
            confidence = random.uniform(*self.config.confidence_range)

            results.append(TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                status=TranslationStatus.SUCCESS,
                confidence=confidence,
                metadata={
                    'mock': True,
                    'delay': delay,
                    'batch_index': i,
                    'translator': 'Mock'
                }
            ))

        return results

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
            Estimated cost (always 0 for mock)
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
            'max_batch_size': 1000,  # No limit
            'rate_limit': 'None (mock)',
            'delay_range': self.config.delay_range,
            'error_rate': self.config.error_rate,
            'confidence_range': self.config.confidence_range,
        }

    def _generate_mock_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Generate a mock translation for the given text.

        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            Mock translated text
        """
        # Simple mock translation logic
        if source_lang == target_lang:
            return text

        # Add language prefix to indicate translation
        source_name = self.LANGUAGE_MAPPING.get(source_lang, source_lang)
        target_name = self.LANGUAGE_MAPPING.get(target_lang, target_lang)

        # Simple transformations for demonstration
        if target_lang == 'en':
            return f"[EN] {text}"
        elif target_lang == 'zh':
            return f"[中文] {text}"
        elif target_lang == 'ja':
            return f"[日本語] {text}"
        elif target_lang == 'ko':
            return f"[한국어] {text}"
        elif target_lang == 'fr':
            return f"[Français] {text}"
        elif target_lang == 'de':
            return f"[Deutsch] {text}"
        elif target_lang == 'es':
            return f"[Español] {text}"
        elif target_lang == 'it':
            return f"[Italiano] {text}"
        elif target_lang == 'pt':
            return f"[Português] {text}"
        elif target_lang == 'ru':
            return f"[Русский] {text}"
        elif target_lang == 'ar':
            return f"[العربية] {text}"
        elif target_lang == 'hi':
            return f"[हिन्दी] {text}"
        elif target_lang == 'th':
            return f"[ไทย] {text}"
        elif target_lang == 'vi':
            return f"[Tiếng Việt] {text}"
        elif target_lang == 'id':
            return f"[Bahasa Indonesia] {text}"
        elif target_lang == 'ms':
            return f"[Bahasa Melayu] {text}"
        elif target_lang == 'tl':
            return f"[Filipino] {text}"
        elif target_lang == 'tr':
            return f"[Türkçe] {text}"
        elif target_lang == 'pl':
            return f"[Polski] {text}"
        elif target_lang == 'nl':
            return f"[Nederlands] {text}"
        elif target_lang == 'sv':
            return f"[Svenska] {text}"
        elif target_lang == 'da':
            return f"[Dansk] {text}"
        elif target_lang == 'no':
            return f"[Norsk] {text}"
        elif target_lang == 'fi':
            return f"[Suomi] {text}"
        elif target_lang == 'cs':
            return f"[Čeština] {text}"
        elif target_lang == 'hu':
            return f"[Magyar] {text}"
        elif target_lang == 'ro':
            return f"[Română] {text}"
        elif target_lang == 'bg':
            return f"[Български] {text}"
        elif target_lang == 'hr':
            return f"[Hrvatski] {text}"
        elif target_lang == 'sk':
            return f"[Slovenčina] {text}"
        elif target_lang == 'sl':
            return f"[Slovenščina] {text}"
        elif target_lang == 'et':
            return f"[Eesti] {text}"
        elif target_lang == 'lv':
            return f"[Latviešu] {text}"
        elif target_lang == 'lt':
            return f"[Lietuvių] {text}"
        elif target_lang == 'uk':
            return f"[Українська] {text}"
        elif target_lang == 'be':
            return f"[Беларуская] {text}"
        elif target_lang == 'mk':
            return f"[Македонски] {text}"
        elif target_lang == 'sq':
            return f"[Shqip] {text}"
        elif target_lang == 'sr':
            return f"[Српски] {text}"
        elif target_lang == 'bs':
            return f"[Bosanski] {text}"
        elif target_lang == 'me':
            return f"[Crnogorski] {text}"
        elif target_lang == 'is':
            return f"[Íslenska] {text}"
        elif target_lang == 'ga':
            return f"[Gaeilge] {text}"
        elif target_lang == 'cy':
            return f"[Cymraeg] {text}"
        elif target_lang == 'mt':
            return f"[Malti] {text}"
        elif target_lang == 'eu':
            return f"[Euskera] {text}"
        elif target_lang == 'ca':
            return f"[Català] {text}"
        elif target_lang == 'gl':
            return f"[Galego] {text}"
        elif target_lang == 'af':
            return f"[Afrikaans] {text}"
        elif target_lang == 'sw':
            return f"[Kiswahili] {text}"
        elif target_lang == 'am':
            return f"[አማርኛ] {text}"
        elif target_lang == 'az':
            return f"[Azərbaycan] {text}"
        elif target_lang == 'bn':
            return f"[বাংলা] {text}"
        elif target_lang == 'gu':
            return f"[ગુજરાતી] {text}"
        elif target_lang == 'he':
            return f"[עברית] {text}"
        elif target_lang == 'ka':
            return f"[ქართული] {text}"
        elif target_lang == 'kk':
            return f"[Қазақ] {text}"
        elif target_lang == 'ky':
            return f"[Кыргыз] {text}"
        elif target_lang == 'lo':
            return f"[ລາວ] {text}"
        elif target_lang == 'mn':
            return f"[Монгол] {text}"
        elif target_lang == 'my':
            return f"[မြန်မာ] {text}"
        elif target_lang == 'ne':
            return f"[नेपाली] {text}"
        elif target_lang == 'si':
            return f"[සිංහල] {text}"
        elif target_lang == 'ta':
            return f"[தமிழ்] {text}"
        elif target_lang == 'te':
            return f"[తెలుగు] {text}"
        elif target_lang == 'ur':
            return f"[اردو] {text}"
        elif target_lang == 'uz':
            return f"[O'zbek] {text}"
        else:
            return f"[{target_name}] {text}"
