"""
OpenAI translator for using GPT models for translation.

This translator uses OpenAI's GPT models to provide high-quality translations
with context awareness and natural language understanding.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

from .base import Translator, TranslationResult, TranslationStatus, TranslationError


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI translator."""
    api_key: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 4000
    temperature: float = 0.3
    max_retries: int = 3
    timeout: int = 30
    base_url: Optional[str] = None


class OpenAITranslator(Translator):
    """
    Translator using OpenAI's GPT models for translation.

    This translator provides high-quality translations with context awareness
    and natural language understanding using OpenAI's GPT models.
    """

    # Language code mapping for OpenAI
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

    def __init__(self, config: OpenAIConfig):
        """
        Initialize the OpenAI translator.

        Args:
            config: OpenAI configuration
        """
        if openai is None:
            raise ImportError("openai is required for OpenAI translation. Install with: pip install openai")

        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout
        )

    @property
    def name(self) -> str:
        """Return the name of this translator."""
        return "OpenAI"

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

        # Get language names
        source_name = self.LANGUAGE_MAPPING.get(source_lang, source_lang)
        target_name = self.LANGUAGE_MAPPING.get(target_lang, target_lang)

        # Create translation prompt
        prompt = self._create_translation_prompt(text, source_name, target_name)

        # Get model and parameters
        model = kwargs.get('model', self.config.model)
        temperature = kwargs.get('temperature', self.config.temperature)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the given text accurately while preserving the original meaning, tone, and context. Return only the translated text without any additional explanations or formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.config.timeout
            )

            # Extract translated text
            translated_text = response.choices[0].message.content.strip()

            # Calculate confidence based on response
            confidence = self._calculate_confidence(response)

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                status=TranslationStatus.SUCCESS,
                confidence=confidence,
                metadata={
                    'model': model,
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'usage': response.usage.dict() if response.usage else None,
                    'finish_reason': response.choices[0].finish_reason,
                    'translator': 'OpenAI'
                }
            )

        except Exception as e:
            raise TranslationError(
                f"OpenAI translation failed: {str(e)}",
                translator_name="OpenAI",
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

        # Get language names
        source_name = self.LANGUAGE_MAPPING.get(source_lang, source_lang)
        target_name = self.LANGUAGE_MAPPING.get(target_lang, target_lang)

        # Create batch translation prompt
        prompt = self._create_batch_translation_prompt(texts, source_name, target_name)

        # Get model and parameters
        model = kwargs.get('model', self.config.model)
        temperature = kwargs.get('temperature', self.config.temperature)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the given texts accurately while preserving the original meaning, tone, and context. Return the translations as a JSON array with the same order as the input texts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.config.timeout
            )

            # Extract translated texts
            translated_texts = self._parse_batch_response(response.choices[0].message.content)

            # Create results
            results = []
            for i, (original_text, translated_text) in enumerate(zip(texts, translated_texts)):
                results.append(TranslationResult(
                    original_text=original_text,
                    translated_text=translated_text,
                    source_language=source_lang,
                    target_language=target_lang,
                    status=TranslationStatus.SUCCESS,
                    confidence=0.9,  # Default confidence for batch
                    metadata={
                        'model': model,
                        'temperature': temperature,
                        'max_tokens': max_tokens,
                        'batch_index': i,
                        'translator': 'OpenAI'
                    }
                ))

            return results

        except Exception as e:
            raise TranslationError(
                f"OpenAI batch translation failed: {str(e)}",
                translator_name="OpenAI",
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
        # Rough cost estimation based on token count
        # This is a simplified estimation and may not be accurate
        char_count = len(text)
        token_count = char_count / 4  # Rough approximation

        # GPT-3.5-turbo pricing (as of 2024)
        cost_per_token = 0.0005 / 1000  # $0.0005 per 1K tokens

        return token_count * cost_per_token

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
            'cost_per_token': 0.0005 / 1000,  # GPT-3.5-turbo pricing
            'cost_per_character': 0.0005 / 4000,  # Rough estimate: ~4 chars per token
            'max_batch_size': 100,
            'rate_limit': '60 requests per minute',
            'model': self.config.model,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
        }

    def _create_translation_prompt(self, text: str, source_name: str, target_name: str) -> str:
        """
        Create a translation prompt for OpenAI.

        Args:
            text: Text to translate
            source_name: Source language name
            target_name: Target language name

        Returns:
            Translation prompt
        """
        return f"Translate the following text from {source_name} to {target_name}:\n\n{text}"

    def _create_batch_translation_prompt(self, texts: List[str], source_name: str, target_name: str) -> str:
        """
        Create a batch translation prompt for OpenAI.

        Args:
            texts: List of texts to translate
            source_name: Source language name
            target_name: Target language name

        Returns:
            Batch translation prompt
        """
        prompt = f"Translate the following texts from {source_name} to {target_name}:\n\n"
        for i, text in enumerate(texts):
            prompt += f"{i+1}. {text}\n"
        prompt += "\nReturn the translations as a JSON array in the same order."
        return prompt

    def _parse_batch_response(self, response: str) -> List[str]:
        """
        Parse the batch translation response from OpenAI.

        Args:
            response: Response from OpenAI

        Returns:
            List of translated texts
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            if isinstance(data, list):
                return data
            else:
                raise ValueError("Response is not a list")
        except (json.JSONDecodeError, ValueError):
            # Fallback: split by lines and clean up
            lines = response.strip().split('\n')
            translated_texts = []
            for line in lines:
                # Remove numbering and clean up
                cleaned = line.strip()
                if cleaned and not cleaned.isdigit():
                    # Remove common prefixes
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.']:
                        if cleaned.startswith(prefix):
                            cleaned = cleaned[len(prefix):].strip()
                            break
                    translated_texts.append(cleaned)
            return translated_texts

    def _calculate_confidence(self, response: Any) -> float:
        """
        Calculate confidence score based on the response.

        Args:
            response: OpenAI response object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        confidence = 0.9

        # Adjust based on finish reason
        if hasattr(response, 'choices') and response.choices:
            finish_reason = response.choices[0].finish_reason
            if finish_reason == 'stop':
                confidence = 1.0
            elif finish_reason == 'length':
                confidence = 0.8
            elif finish_reason == 'content_filter':
                confidence = 0.6

        return confidence
