//! Mock translator for testing and development

use crate::{TranslationError, TranslationResult, Translator};
use async_trait::async_trait;
use rand::Rng;
use std::collections::HashMap;
use std::time::Duration;
use tokio::time::sleep;

/// Configuration for Mock translator
#[derive(Debug, Clone)]
pub struct MockConfig {
    /// Random delay range in milliseconds (min, max)
    pub delay_range: (u64, u64),
    /// Probability of errors (0.0 to 1.0)
    pub error_rate: f64,
    /// Random confidence range (min, max)
    pub confidence_range: (f64, f64),
}

impl Default for MockConfig {
    fn default() -> Self {
        Self {
            delay_range: (100, 500), // 100-500ms
            error_rate: 0.0,         // No errors by default
            confidence_range: (0.8, 1.0),
        }
    }
}

/// Mock translator for testing and development
pub struct MockTranslator {
    config: MockConfig,
    language_mapping: HashMap<String, String>,
}

impl MockTranslator {
    /// Create a new mock translator with default config
    pub fn new() -> Self {
        Self::with_config(MockConfig::default())
    }

    /// Create a new mock translator with custom config
    pub fn with_config(config: MockConfig) -> Self {
        let mut language_mapping = HashMap::new();

        // Add language mappings
        let languages = [
            ("en", "English"),
            ("zh", "Chinese"),
            ("ja", "Japanese"),
            ("ko", "Korean"),
            ("fr", "French"),
            ("de", "German"),
            ("es", "Spanish"),
            ("it", "Italian"),
            ("pt", "Portuguese"),
            ("ru", "Russian"),
            ("ar", "Arabic"),
            ("hi", "Hindi"),
            ("th", "Thai"),
            ("vi", "Vietnamese"),
            ("id", "Indonesian"),
        ];

        for (code, name) in &languages {
            language_mapping.insert(code.to_string(), name.to_string());
        }

        Self {
            config,
            language_mapping,
        }
    }

    /// Generate a mock translation
    fn generate_mock_translation(&self, text: &str, source: &str, target: &str) -> String {
        if source == target {
            return text.to_string();
        }

        // Get language name for prefix
        let target_name = self
            .language_mapping
            .get(target)
            .map(|s| s.as_str())
            .unwrap_or(target);

        // Generate mock translation with language prefix
        match target {
            "en" => format!("[EN] {}", text),
            "zh" => format!("[中文] {}", text),
            "ja" => format!("[日本語] {}", text),
            "ko" => format!("[한국어] {}", text),
            "fr" => format!("[Français] {}", text),
            "de" => format!("[Deutsch] {}", text),
            "es" => format!("[Español] {}", text),
            "it" => format!("[Italiano] {}", text),
            "pt" => format!("[Português] {}", text),
            "ru" => format!("[Русский] {}", text),
            "ar" => format!("[العربية] {}", text),
            "hi" => format!("[हिन्दी] {}", text),
            "th" => format!("[ไทย] {}", text),
            "vi" => format!("[Tiếng Việt] {}", text),
            "id" => format!("[Bahasa Indonesia] {}", text),
            _ => format!("[{}] {}", target_name, text),
        }
    }
}

impl Default for MockTranslator {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl Translator for MockTranslator {
    fn name(&self) -> &'static str {
        "Mock"
    }

    fn supported_languages(&self) -> Vec<String> {
        self.language_mapping.keys().cloned().collect()
    }

    async fn translate(
        &self,
        text: &str,
        source_language: &str,
        target_language: &str,
    ) -> Result<TranslationResult, TranslationError> {
        // Validate languages
        self.validate_languages(source_language, target_language)?;

        // Normalize language codes
        let source_lang = self.normalize_language_code(source_language);
        let target_lang = self.normalize_language_code(target_language);

        // Generate random values before await
        let (delay_ms, random_val, confidence) = {
            let mut rng = rand::thread_rng();
            let delay = rng.gen_range(self.config.delay_range.0..=self.config.delay_range.1);
            let random = rng.gen::<f64>();
            let conf =
                rng.gen_range(self.config.confidence_range.0..=self.config.confidence_range.1);
            (delay, random, conf)
        };

        // Simulate API delay
        sleep(Duration::from_millis(delay_ms)).await;

        // Simulate errors
        if random_val < self.config.error_rate {
            return Err(TranslationError::TranslationFailed {
                message: "Mock translation failed (simulated error)".to_string(),
                translator_name: "Mock".to_string(),
                error_code: Some("MOCK_ERROR".to_string()),
            });
        }

        // Generate mock translation
        let translated_text = self.generate_mock_translation(text, &source_lang, &target_lang);

        let mut result = TranslationResult::success(
            text.to_string(),
            translated_text,
            source_lang,
            target_lang,
            confidence,
        );

        // Add metadata
        result = result
            .with_metadata("mock".to_string(), "true".to_string())
            .with_metadata("delay_ms".to_string(), delay_ms.to_string())
            .with_metadata("translator".to_string(), "Mock".to_string());

        Ok(result)
    }

    async fn translate_batch(
        &self,
        texts: &[String],
        source_language: &str,
        target_language: &str,
    ) -> Result<Vec<TranslationResult>, TranslationError> {
        // Validate languages
        self.validate_languages(source_language, target_language)?;

        // Normalize language codes
        let source_lang = self.normalize_language_code(source_language);
        let target_lang = self.normalize_language_code(target_language);

        // Generate random values before await
        let (delay_ms, random_val) = {
            let mut rng = rand::thread_rng();
            let delay = rng.gen_range(self.config.delay_range.0..=self.config.delay_range.1);
            let random = rng.gen::<f64>();
            (delay, random)
        };

        // Simulate API delay
        sleep(Duration::from_millis(delay_ms)).await;

        // Simulate errors
        if random_val < self.config.error_rate {
            return Err(TranslationError::TranslationFailed {
                message: "Mock batch translation failed (simulated error)".to_string(),
                translator_name: "Mock".to_string(),
                error_code: Some("MOCK_BATCH_ERROR".to_string()),
            });
        }

        // Generate mock translations
        let mut results = Vec::new();
        for (i, text) in texts.iter().enumerate() {
            let translated_text = self.generate_mock_translation(text, &source_lang, &target_lang);
            let confidence = {
                let mut rng = rand::thread_rng();
                rng.gen_range(self.config.confidence_range.0..=self.config.confidence_range.1)
            };

            let mut result = TranslationResult::success(
                text.to_string(),
                translated_text,
                source_lang.clone(),
                target_lang.clone(),
                confidence,
            );

            result = result
                .with_metadata("mock".to_string(), "true".to_string())
                .with_metadata("delay_ms".to_string(), delay_ms.to_string())
                .with_metadata("batch_index".to_string(), i.to_string())
                .with_metadata("translator".to_string(), "Mock".to_string());

            results.push(result);
        }

        Ok(results)
    }

    fn normalize_language_code(&self, language_code: &str) -> String {
        let normalized = language_code.to_lowercase();

        // Handle common variations
        match normalized.as_str() {
            "en-us" | "en-gb" => "en".to_string(),
            "zh-cn" | "zh-tw" => "zh".to_string(),
            "ja-jp" => "ja".to_string(),
            "ko-kr" => "ko".to_string(),
            "fr-fr" => "fr".to_string(),
            "de-de" => "de".to_string(),
            "es-es" => "es".to_string(),
            "it-it" => "it".to_string(),
            "pt-br" | "pt-pt" => "pt".to_string(),
            "ru-ru" => "ru".to_string(),
            "ar-sa" => "ar".to_string(),
            "hi-in" => "hi".to_string(),
            "th-th" => "th".to_string(),
            "vi-vn" => "vi".to_string(),
            "id-id" => "id".to_string(),
            _ => normalized,
        }
    }

    fn estimate_cost(&self, _text: &str, _source: &str, _target: &str) -> f64 {
        0.0 // Mock is free
    }

    fn get_usage_info(&self) -> HashMap<String, String> {
        let mut info = HashMap::new();
        info.insert("name".to_string(), self.name().to_string());
        info.insert(
            "languages".to_string(),
            self.supported_languages().len().to_string(),
        );
        info.insert("cost_per_character".to_string(), "0.0".to_string());
        info.insert("max_batch_size".to_string(), "1000".to_string());
        info.insert("rate_limit".to_string(), "None (mock)".to_string());
        info.insert(
            "delay_range".to_string(),
            format!(
                "{}-{}ms",
                self.config.delay_range.0, self.config.delay_range.1
            ),
        );
        info.insert("error_rate".to_string(), self.config.error_rate.to_string());
        info
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::TranslationStatus;

    #[test]
    fn test_mock_config_default() {
        let config = MockConfig::default();
        assert_eq!(config.delay_range, (100, 500));
        assert_eq!(config.error_rate, 0.0);
        assert_eq!(config.confidence_range, (0.8, 1.0));
    }

    #[test]
    fn test_mock_translator_new() {
        let translator = MockTranslator::new();
        assert_eq!(translator.name(), "Mock");
    }

    #[test]
    fn test_mock_translator_default() {
        let translator = MockTranslator::default();
        assert_eq!(translator.name(), "Mock");
    }

    #[test]
    fn test_mock_translator_with_config() {
        let config = MockConfig {
            delay_range: (10, 50),
            error_rate: 0.5,
            confidence_range: (0.5, 0.9),
        };
        let translator = MockTranslator::with_config(config);
        assert_eq!(translator.name(), "Mock");
    }

    #[test]
    fn test_supported_languages() {
        let translator = MockTranslator::new();
        let languages = translator.supported_languages();

        assert!(!languages.is_empty());
        assert!(languages.contains(&"en".to_string()));
        assert!(languages.contains(&"zh".to_string()));
        assert!(languages.contains(&"ja".to_string()));
        assert!(languages.contains(&"ko".to_string()));
    }

    #[tokio::test]
    async fn test_mock_translate() {
        let translator = MockTranslator::new();
        let result = translator
            .translate("Hello world", "en", "zh")
            .await
            .unwrap();

        assert_eq!(result.original_text, "Hello world");
        assert!(result.translated_text.contains("Hello world"));
        assert_eq!(result.source_language, "en");
        assert_eq!(result.target_language, "zh");
        assert_eq!(result.status, TranslationStatus::Success);
        assert!(result.confidence > 0.0);
        assert!(result.confidence >= 0.8 && result.confidence <= 1.0);
    }

    #[tokio::test]
    async fn test_mock_translate_same_language() {
        let translator = MockTranslator::new();
        let result = translator.translate("Hello", "en", "en").await.unwrap();

        assert_eq!(result.original_text, "Hello");
        assert_eq!(result.translated_text, "Hello");
    }

    #[tokio::test]
    async fn test_mock_translate_different_languages() {
        let translator = MockTranslator::new();

        let lang_pairs = vec![
            ("en", "zh"),
            ("en", "ja"),
            ("en", "ko"),
            ("zh", "en"),
            ("ja", "en"),
            ("ko", "en"),
            ("fr", "de"),
            ("es", "it"),
        ];

        for (source, target) in lang_pairs {
            let result = translator.translate("test", source, target).await.unwrap();
            assert_eq!(result.status, TranslationStatus::Success);
            assert_eq!(result.source_language, source);
            assert_eq!(result.target_language, target);
        }
    }

    #[tokio::test]
    async fn test_mock_translate_batch() {
        let translator = MockTranslator::new();
        let texts = vec!["Hello".to_string(), "World".to_string(), "Test".to_string()];

        let results = translator
            .translate_batch(&texts, "en", "zh")
            .await
            .unwrap();

        assert_eq!(results.len(), 3);
        for (i, result) in results.iter().enumerate() {
            assert_eq!(result.status, TranslationStatus::Success);
            assert!(result.confidence > 0.0);
            assert_eq!(result.original_text, texts[i]);
        }
    }

    #[tokio::test]
    async fn test_mock_translate_batch_empty() {
        let translator = MockTranslator::new();
        let texts: Vec<String> = vec![];

        let results = translator
            .translate_batch(&texts, "en", "zh")
            .await
            .unwrap();

        assert_eq!(results.len(), 0);
    }

    #[tokio::test]
    async fn test_mock_translate_batch_large() {
        let translator = MockTranslator::new();
        let texts: Vec<String> = (0..100).map(|i| format!("Text {}", i)).collect();

        let results = translator
            .translate_batch(&texts, "en", "zh")
            .await
            .unwrap();

        assert_eq!(results.len(), 100);
    }

    #[tokio::test]
    async fn test_mock_translate_error() {
        let config = MockConfig {
            delay_range: (10, 20),
            error_rate: 1.0, // Always fail
            confidence_range: (0.8, 1.0),
        };
        let translator = MockTranslator::with_config(config);

        let result = translator.translate("Hello", "en", "zh").await;
        assert!(result.is_err());

        match result {
            Err(TranslationError::TranslationFailed { message, .. }) => {
                assert!(message.contains("simulated error"));
            }
            _ => panic!("Expected TranslationFailed error"),
        }
    }

    #[tokio::test]
    async fn test_mock_translate_batch_error() {
        let config = MockConfig {
            delay_range: (10, 20),
            error_rate: 1.0,
            confidence_range: (0.8, 1.0),
        };
        let translator = MockTranslator::with_config(config);

        let texts = vec!["Hello".to_string()];
        let result = translator.translate_batch(&texts, "en", "zh").await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_unsupported_language() {
        let translator = MockTranslator::new();
        let result = translator.translate("Hello", "en", "xyz").await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_unsupported_source_language() {
        let translator = MockTranslator::new();
        let result = translator.translate("Hello", "xyz", "en").await;
        assert!(result.is_err());
    }

    #[test]
    fn test_normalize_language_code() {
        let translator = MockTranslator::new();

        assert_eq!(translator.normalize_language_code("en-US"), "en");
        assert_eq!(translator.normalize_language_code("en-GB"), "en");
        assert_eq!(translator.normalize_language_code("zh-CN"), "zh");
        assert_eq!(translator.normalize_language_code("zh-TW"), "zh");
        assert_eq!(translator.normalize_language_code("ja-JP"), "ja");
        assert_eq!(translator.normalize_language_code("ko-KR"), "ko");
        assert_eq!(translator.normalize_language_code("fr-FR"), "fr");
        assert_eq!(translator.normalize_language_code("de-DE"), "de");
        assert_eq!(translator.normalize_language_code("pt-BR"), "pt");
        assert_eq!(translator.normalize_language_code("pt-PT"), "pt");

        // Case insensitive
        assert_eq!(translator.normalize_language_code("EN-US"), "en");
        assert_eq!(translator.normalize_language_code("ZH-CN"), "zh");

        // Unknown codes should be returned as-is (lowercased)
        assert_eq!(translator.normalize_language_code("xyz"), "xyz");
    }

    #[test]
    fn test_estimate_cost() {
        let translator = MockTranslator::new();

        assert_eq!(translator.estimate_cost("test", "en", "zh"), 0.0);
        assert_eq!(translator.estimate_cost("long text here", "zh", "en"), 0.0);
        assert_eq!(translator.estimate_cost("", "en", "zh"), 0.0);
    }

    #[test]
    fn test_get_usage_info() {
        let translator = MockTranslator::new();
        let info = translator.get_usage_info();

        assert_eq!(info.get("name").unwrap(), "Mock");
        assert_eq!(info.get("cost_per_character").unwrap(), "0.0");
        assert_eq!(info.get("max_batch_size").unwrap(), "1000");
        assert!(info.contains_key("languages"));
        assert!(info.contains_key("rate_limit"));
        assert!(info.contains_key("delay_range"));
        assert!(info.contains_key("error_rate"));
    }

    #[test]
    fn test_generate_mock_translation() {
        let translator = MockTranslator::new();

        // Test different target languages
        let text = "Hello";

        let en = translator.generate_mock_translation(text, "zh", "en");
        assert!(en.contains("[EN]"));
        assert!(en.contains(text));

        let zh = translator.generate_mock_translation(text, "en", "zh");
        assert!(zh.contains("[中文]"));

        let ja = translator.generate_mock_translation(text, "en", "ja");
        assert!(ja.contains("[日本語]"));

        let ko = translator.generate_mock_translation(text, "en", "ko");
        assert!(ko.contains("[한국어]"));
    }

    #[test]
    fn test_generate_mock_translation_same_language() {
        let translator = MockTranslator::new();
        let text = "Hello";
        let result = translator.generate_mock_translation(text, "en", "en");
        assert_eq!(result, text);
    }

    #[tokio::test]
    async fn test_translation_metadata() {
        let translator = MockTranslator::new();
        let result = translator.translate("test", "en", "zh").await.unwrap();

        let metadata = result.metadata.as_ref().unwrap();
        assert_eq!(metadata.get("mock"), Some(&"true".to_string()));
        assert_eq!(metadata.get("translator"), Some(&"Mock".to_string()));
        assert!(metadata.contains_key("delay_ms"));
    }

    #[tokio::test]
    async fn test_batch_translation_metadata() {
        let translator = MockTranslator::new();
        let texts = vec!["test1".to_string(), "test2".to_string()];
        let results = translator
            .translate_batch(&texts, "en", "zh")
            .await
            .unwrap();

        for (i, result) in results.iter().enumerate() {
            let metadata = result.metadata.as_ref().unwrap();
            assert_eq!(metadata.get("mock"), Some(&"true".to_string()));
            assert_eq!(metadata.get("batch_index"), Some(&i.to_string()));
        }
    }

    #[tokio::test]
    async fn test_custom_confidence_range() {
        let config = MockConfig {
            delay_range: (10, 20),
            error_rate: 0.0,
            confidence_range: (0.5, 0.6),
        };
        let translator = MockTranslator::with_config(config);

        let result = translator.translate("test", "en", "zh").await.unwrap();
        assert!(result.confidence >= 0.5 && result.confidence <= 0.6);
    }

    #[tokio::test]
    async fn test_zero_delay() {
        let config = MockConfig {
            delay_range: (0, 0),
            error_rate: 0.0,
            confidence_range: (0.8, 1.0),
        };
        let translator = MockTranslator::with_config(config);

        let result = translator.translate("test", "en", "zh").await.unwrap();
        assert_eq!(result.status, TranslationStatus::Success);
    }

    #[tokio::test]
    async fn test_empty_text() {
        let translator = MockTranslator::new();
        let result = translator.translate("", "en", "zh").await.unwrap();

        assert_eq!(result.original_text, "");
        assert!(result.translated_text.contains(""));
    }
}
