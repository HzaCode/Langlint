//! Google Translate translator using the free API

use crate::{TranslationError, TranslationResult, Translator};
use async_trait::async_trait;
use rand::Rng;
use serde::Deserialize;
use std::collections::HashMap;
use std::time::Duration;
use tokio::time::sleep;

/// Configuration for Google translator
#[derive(Debug, Clone)]
pub struct GoogleConfig {
    /// Timeout for requests in seconds
    pub timeout: u64,
    /// Retry count for failed requests
    pub retry_count: u32,
    /// Random delay range in milliseconds (to avoid rate limiting)
    pub delay_range: (u64, u64),
    /// Custom service URLs (if any)
    pub service_urls: Option<Vec<String>>,
}

impl Default for GoogleConfig {
    fn default() -> Self {
        Self {
            timeout: 30,
            retry_count: 3,
            delay_range: (300, 600), // 300-600ms to respect rate limits
            service_urls: None,
        }
    }
}

/// Google Translate API response
#[derive(Debug, Deserialize)]
#[allow(dead_code)]
struct GoogleTranslateResponse {
    #[serde(rename = "sentences")]
    sentences: Option<Vec<Sentence>>,
    #[serde(rename = "src")]
    detected_language: Option<String>,
}

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
struct Sentence {
    trans: Option<String>,
    orig: Option<String>,
}

/// Google Translator implementation
pub struct GoogleTranslator {
    config: GoogleConfig,
    client: reqwest::Client,
    language_mapping: HashMap<String, String>,
}

impl GoogleTranslator {
    /// Create a new Google translator with default config
    pub fn new() -> Result<Self, TranslationError> {
        Self::with_config(GoogleConfig::default())
    }

    /// Create a new Google translator with custom config
    pub fn with_config(config: GoogleConfig) -> Result<Self, TranslationError> {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(config.timeout))
            .build()
            .map_err(TranslationError::NetworkError)?;

        let mut language_mapping = HashMap::new();

        // Add supported languages (subset for now, can be expanded)
        let languages = [
            ("en", "english"),
            ("zh", "chinese (simplified)"),
            ("zh-cn", "chinese (simplified)"),
            ("zh-tw", "chinese (traditional)"),
            ("ja", "japanese"),
            ("ko", "korean"),
            ("fr", "french"),
            ("de", "german"),
            ("es", "spanish"),
            ("it", "italian"),
            ("pt", "portuguese"),
            ("ru", "russian"),
            ("ar", "arabic"),
            ("hi", "hindi"),
            ("th", "thai"),
            ("vi", "vietnamese"),
            ("id", "indonesian"),
            ("nl", "dutch"),
            ("sv", "swedish"),
            ("da", "danish"),
            ("no", "norwegian"),
            ("fi", "finnish"),
            ("pl", "polish"),
            ("tr", "turkish"),
            ("cs", "czech"),
            ("hu", "hungarian"),
            ("ro", "romanian"),
            ("bg", "bulgarian"),
            ("el", "greek"),
            ("he", "hebrew"),
            ("uk", "ukrainian"),
        ];

        for (code, name) in &languages {
            language_mapping.insert(code.to_string(), name.to_string());
        }

        Ok(Self {
            config,
            client,
            language_mapping,
        })
    }

    /// Internal method to call Google Translate API
    async fn call_google_api(
        &self,
        text: &str,
        source_lang: &str,
        target_lang: &str,
    ) -> Result<String, TranslationError> {
        // Use Google Translate's free endpoint
        let url = "https://translate.googleapis.com/translate_a/single";

        let params = [
            ("client", "gtx"),
            ("sl", source_lang),
            ("tl", target_lang),
            ("dt", "t"),
            ("q", text),
        ];

        let response = self
            .client
            .get(url)
            .query(&params)
            .send()
            .await
            .map_err(TranslationError::NetworkError)?;

        if !response.status().is_success() {
            return Err(TranslationError::TranslationFailed {
                message: format!("HTTP error: {}", response.status()),
                translator_name: "Google Translate".to_string(),
                error_code: Some(response.status().to_string()),
            });
        }

        // Parse response as JSON
        let json: serde_json::Value =
            response
                .json()
                .await
                .map_err(|e| TranslationError::TranslationFailed {
                    message: format!("Failed to parse response: {}", e),
                    translator_name: "Google Translate".to_string(),
                    error_code: Some("PARSE_ERROR".to_string()),
                })?;

        // Extract translation from nested array structure
        // Response format: [[[translated_text, original_text, null, null, ...]], ...]
        let translated_text = json
            .get(0)
            .and_then(|arr| arr.get(0))
            .and_then(|sentence| sentence.get(0))
            .and_then(|text| text.as_str())
            .ok_or_else(|| TranslationError::TranslationFailed {
                message: "Failed to extract translation from response".to_string(),
                translator_name: "Google Translate".to_string(),
                error_code: Some("EXTRACTION_ERROR".to_string()),
            })?;

        Ok(translated_text.to_string())
    }
}

impl Default for GoogleTranslator {
    fn default() -> Self {
        Self::new().expect("Failed to create GoogleTranslator")
    }
}

#[async_trait]
impl Translator for GoogleTranslator {
    fn name(&self) -> &'static str {
        "Google Translate"
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
        // Validate input
        if text.trim().is_empty() {
            return Err(TranslationError::InvalidInput(
                "Text cannot be empty".to_string(),
            ));
        }

        // Validate languages
        self.validate_languages(source_language, target_language)?;

        // Normalize language codes
        let source_lang = self.normalize_language_code(source_language);
        let target_lang = self.normalize_language_code(target_language);

        // Add random delay to avoid rate limiting
        let delay_ms = {
            let mut rng = rand::thread_rng();
            rng.gen_range(self.config.delay_range.0..=self.config.delay_range.1)
        };
        sleep(Duration::from_millis(delay_ms)).await;

        // Retry logic
        let mut last_error = None;
        for attempt in 0..self.config.retry_count {
            match self.call_google_api(text, &source_lang, &target_lang).await {
                Ok(translated_text) => {
                    let mut result = TranslationResult::success(
                        text.to_string(),
                        translated_text,
                        source_lang,
                        target_lang,
                        0.9, // Default confidence for Google Translate
                    );

                    result = result
                        .with_metadata("translator".to_string(), "Google Translate".to_string())
                        .with_metadata("attempt".to_string(), (attempt + 1).to_string())
                        .with_metadata("delay_ms".to_string(), delay_ms.to_string());

                    return Ok(result);
                }
                Err(e) => {
                    last_error = Some(e);
                    if attempt < self.config.retry_count - 1 {
                        // Wait before retry
                        sleep(Duration::from_millis(500 * (attempt as u64 + 1))).await;
                    }
                }
            }
        }

        // All retries failed
        Err(
            last_error.unwrap_or_else(|| TranslationError::TranslationFailed {
                message: "Unknown error".to_string(),
                translator_name: "Google Translate".to_string(),
                error_code: None,
            }),
        )
    }

    async fn translate_batch(
        &self,
        texts: &[String],
        source_language: &str,
        target_language: &str,
    ) -> Result<Vec<TranslationResult>, TranslationError> {
        // Validate languages
        self.validate_languages(source_language, target_language)?;

        // Translate texts concurrently with limited concurrency
        // Use tokio semaphore to limit to 3 concurrent requests
        use std::sync::Arc;
        use tokio::sync::Semaphore;

        let semaphore = Arc::new(Semaphore::new(3));
        let mut tasks = Vec::new();

        for (index, text) in texts.iter().enumerate() {
            let text = text.clone();
            let source = source_language.to_string();
            let target = target_language.to_string();
            let semaphore = semaphore.clone();
            let translator = self;

            let task = async move {
                let _permit = semaphore.acquire().await.unwrap();

                match translator.translate(&text, &source, &target).await {
                    Ok(mut result) => {
                        result = result.with_metadata("batch_index".to_string(), index.to_string());
                        result
                    }
                    Err(_e) => {
                        // On error, return failed result with original text
                        TranslationResult::failed(
                            text.clone(),
                            source.clone(),
                            target.clone(),
                            "Translation failed in batch".to_string(),
                        )
                        .with_metadata("batch_index".to_string(), index.to_string())
                    }
                }
            };

            tasks.push(task);
        }

        // Wait for all tasks to complete
        let results = futures::future::join_all(tasks).await;
        Ok(results)
    }

    fn normalize_language_code(&self, language_code: &str) -> String {
        let normalized = language_code.to_lowercase();

        // Handle common variations
        match normalized.as_str() {
            "en-us" | "en-gb" => "en".to_string(),
            "zh" => "zh-cn".to_string(), // Default to simplified Chinese
            "zh-cn" => "zh-cn".to_string(),
            "zh-tw" => "zh-tw".to_string(),
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
        0.0 // Google Translate free tier
    }

    fn get_usage_info(&self) -> HashMap<String, String> {
        let mut info = HashMap::new();
        info.insert("name".to_string(), self.name().to_string());
        info.insert(
            "languages".to_string(),
            self.supported_languages().len().to_string(),
        );
        info.insert("cost_per_character".to_string(), "0.0".to_string());
        info.insert("max_batch_size".to_string(), "100".to_string());
        info.insert(
            "rate_limit".to_string(),
            "Limited (delays added)".to_string(),
        );
        info.insert("timeout".to_string(), format!("{}s", self.config.timeout));
        info.insert(
            "retry_count".to_string(),
            self.config.retry_count.to_string(),
        );
        info
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::TranslationStatus;

    #[tokio::test]
    #[ignore] // Ignore by default as it requires network access
    async fn test_google_translate() {
        let translator = GoogleTranslator::new().unwrap();
        let result = translator
            .translate("Hello world", "en", "zh")
            .await
            .unwrap();

        assert_eq!(result.original_text, "Hello world");
        assert!(!result.translated_text.is_empty());
        assert_eq!(result.status, TranslationStatus::Success);
    }

    #[tokio::test]
    #[ignore] // Ignore by default as it requires network access
    async fn test_google_translate_batch() {
        let translator = GoogleTranslator::new().unwrap();
        let texts = vec!["Hello".to_string(), "World".to_string(), "Test".to_string()];

        let results = translator
            .translate_batch(&texts, "en", "zh")
            .await
            .unwrap();

        assert_eq!(results.len(), 3);
        for result in results {
            assert!(!result.translated_text.is_empty());
        }
    }

    #[test]
    fn test_normalize_language_code() {
        let translator = GoogleTranslator::new().unwrap();
        assert_eq!(translator.normalize_language_code("en-US"), "en");
        assert_eq!(translator.normalize_language_code("zh"), "zh-cn");
        assert_eq!(translator.normalize_language_code("zh-CN"), "zh-cn");
    }
}
