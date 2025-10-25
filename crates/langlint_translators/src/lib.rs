//! Translation services for Langlint
//!
//! This module provides a unified interface for translation services,
//! including mock and real translators like Google Translate.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

pub mod google;
pub mod mock;

pub use google::GoogleTranslator;
pub use mock::MockTranslator;

/// Translation status enum
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TranslationStatus {
    Success,
    Failed,
    Partial,
    Skipped,
}

/// Result of a translation operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TranslationResult {
    /// The original text that was translated
    pub original_text: String,
    /// The translated text
    pub translated_text: String,
    /// Source language code
    pub source_language: String,
    /// Target language code
    pub target_language: String,
    /// Status of the translation
    pub status: TranslationStatus,
    /// Confidence score (0.0 to 1.0)
    pub confidence: f64,
    /// Additional metadata about the translation
    pub metadata: Option<HashMap<String, String>>,
}

impl TranslationResult {
    /// Create a new successful translation result
    pub fn success(
        original_text: String,
        translated_text: String,
        source_language: String,
        target_language: String,
        confidence: f64,
    ) -> Self {
        Self {
            original_text,
            translated_text,
            source_language,
            target_language,
            status: TranslationStatus::Success,
            confidence,
            metadata: None,
        }
    }

    /// Create a failed translation result
    pub fn failed(
        original_text: String,
        source_language: String,
        target_language: String,
        error_msg: String,
    ) -> Self {
        let mut metadata = HashMap::new();
        metadata.insert("error".to_string(), error_msg);

        Self {
            original_text: original_text.clone(),
            translated_text: original_text, // Fallback to original
            source_language,
            target_language,
            status: TranslationStatus::Failed,
            confidence: 0.0,
            metadata: Some(metadata),
        }
    }

    /// Add metadata to the result
    pub fn with_metadata(mut self, key: String, value: String) -> Self {
        self.metadata
            .get_or_insert_with(HashMap::new)
            .insert(key, value);
        self
    }
}

/// Translation error type
#[derive(Error, Debug)]
pub enum TranslationError {
    #[error("Language '{0}' is not supported")]
    UnsupportedLanguage(String),

    #[error("Translation failed: {message}")]
    TranslationFailed {
        message: String,
        translator_name: String,
        error_code: Option<String>,
    },

    #[error("Network error: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("Invalid input: {0}")]
    InvalidInput(String),

    #[error("Rate limit exceeded")]
    RateLimitExceeded,

    #[error("Other error: {0}")]
    Other(#[from] anyhow::Error),
}

/// Translator trait that all translators must implement
#[async_trait]
pub trait Translator: Send + Sync {
    /// Return the name of this translator
    fn name(&self) -> &'static str;

    /// Return a list of supported language codes
    fn supported_languages(&self) -> Vec<String>;

    /// Check if a language code is supported
    fn is_language_supported(&self, language_code: &str) -> bool {
        let normalized = self.normalize_language_code(language_code);
        self.supported_languages()
            .iter()
            .any(|lang| lang == &normalized)
    }

    /// Normalize a language code to the format expected by this translator
    fn normalize_language_code(&self, language_code: &str) -> String {
        language_code.to_lowercase()
    }

    /// Validate that both source and target languages are supported
    fn validate_languages(&self, source: &str, target: &str) -> Result<(), TranslationError> {
        if !self.is_language_supported(source) {
            return Err(TranslationError::UnsupportedLanguage(source.to_string()));
        }
        if !self.is_language_supported(target) {
            return Err(TranslationError::UnsupportedLanguage(target.to_string()));
        }
        Ok(())
    }

    /// Translate text from source language to target language
    async fn translate(
        &self,
        text: &str,
        source_language: &str,
        target_language: &str,
    ) -> Result<TranslationResult, TranslationError>;

    /// Translate multiple texts in a single batch operation
    async fn translate_batch(
        &self,
        texts: &[String],
        source_language: &str,
        target_language: &str,
    ) -> Result<Vec<TranslationResult>, TranslationError>;

    /// Estimate the cost of translating the given text
    fn estimate_cost(&self, text: &str, _source: &str, _target: &str) -> f64 {
        // Default implementation: free
        let _ = text; // Suppress unused warning
        0.0
    }

    /// Get usage information for this translator
    fn get_usage_info(&self) -> HashMap<String, String> {
        let mut info = HashMap::new();
        info.insert("name".to_string(), self.name().to_string());
        info.insert(
            "languages".to_string(),
            format!("{}", self.supported_languages().len()),
        );
        info
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_translation_result_success() {
        let result = TranslationResult::success(
            "Hello".to_string(),
            "你好".to_string(),
            "en".to_string(),
            "zh".to_string(),
            0.95,
        );

        assert_eq!(result.original_text, "Hello");
        assert_eq!(result.translated_text, "你好");
        assert_eq!(result.status, TranslationStatus::Success);
        assert_eq!(result.confidence, 0.95);
    }

    #[test]
    fn test_translation_result_failed() {
        let result = TranslationResult::failed(
            "Hello".to_string(),
            "en".to_string(),
            "zh".to_string(),
            "Network error".to_string(),
        );

        assert_eq!(result.status, TranslationStatus::Failed);
        assert_eq!(result.confidence, 0.0);
        assert!(result.metadata.is_some());
    }

    #[test]
    fn test_translation_result_with_metadata() {
        let result = TranslationResult::success(
            "Hello".to_string(),
            "你好".to_string(),
            "en".to_string(),
            "zh".to_string(),
            0.95,
        )
        .with_metadata("translator".to_string(), "Test".to_string());

        assert!(result.metadata.is_some());
        assert_eq!(
            result.metadata.unwrap().get("translator"),
            Some(&"Test".to_string())
        );
    }
}
