use serde::{Deserialize, Serialize};

/// Types of translatable units
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum UnitType {
    Comment,
    Docstring,
    StringLiteral,
    TextNode,
    Metadata,
}

/// Translation priority levels
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "lowercase")]
pub enum Priority {
    High,
    Medium,
    Low,
    Ignore,
}

impl Default for Priority {
    fn default() -> Self {
        Priority::Medium
    }
}

/// Position in source code
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub struct Position {
    pub line: u32,
    pub column: u32,
}

impl Position {
    pub fn new(line: u32, column: u32) -> Self {
        Self { line, column }
    }
}

/// A unit of text that can be translated
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TranslatableUnit {
    pub content: String,
    pub unit_type: UnitType,
    pub line_number: u32,
    pub column_number: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub context: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<serde_json::Value>,
    #[serde(default)]
    pub priority: Priority,
    /// Detected language code (e.g., "zh-CN", "ja", "en")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub detected_language: Option<String>,
}

impl TranslatableUnit {
    pub fn new(
        content: String,
        unit_type: UnitType,
        line_number: u32,
        column_number: u32,
    ) -> Self {
        Self {
            content,
            unit_type,
            line_number,
            column_number,
            context: None,
            metadata: None,
            priority: Priority::default(),
            detected_language: None,
        }
    }

    pub fn with_context(mut self, context: String) -> Self {
        self.context = Some(context);
        self
    }

    pub fn with_metadata(mut self, metadata: serde_json::Value) -> Self {
        self.metadata = Some(metadata);
        self
    }

    pub fn with_priority(mut self, priority: Priority) -> Self {
        self.priority = priority;
        self
    }

    pub fn with_detected_language(mut self, language: String) -> Self {
        self.detected_language = Some(language);
        self
    }

    /// Detect and set the language of the content
    pub fn detect_language(&mut self) {
        self.detected_language = detect_language(&self.content);
    }
}

/// Detect the language of text content
pub fn detect_language(text: &str) -> Option<String> {
    use whatlang::detect;
    
    // Skip very short text (likely not enough for detection)
    if text.trim().len() < 3 {
        return None;
    }
    
    // Detect language
    if let Some(info) = detect(text) {
        let lang_code = match info.lang() {
            whatlang::Lang::Eng => "en",
            whatlang::Lang::Cmn => "zh-CN", // Mandarin Chinese
            whatlang::Lang::Jpn => "ja",
            whatlang::Lang::Kor => "ko",
            whatlang::Lang::Fra => "fr",
            whatlang::Lang::Deu => "de",
            whatlang::Lang::Spa => "es",
            whatlang::Lang::Por => "pt",
            whatlang::Lang::Rus => "ru",
            whatlang::Lang::Ita => "it",
            whatlang::Lang::Nld => "nl",
            whatlang::Lang::Pol => "pl",
            whatlang::Lang::Swe => "sv",
            whatlang::Lang::Tha => "th",
            whatlang::Lang::Vie => "vi",
            whatlang::Lang::Hin => "hi",
            whatlang::Lang::Ind => "id",
            whatlang::Lang::Ara => "ar",
            whatlang::Lang::Heb => "he",
            whatlang::Lang::Tur => "tr",
            whatlang::Lang::Ell => "el",
            whatlang::Lang::Pes => "fa",
            _ => return None, // Unsupported language
        };
        
        // Only return if confidence is reasonable
        if info.confidence() > 0.7 {
            return Some(lang_code.to_string());
        }
    }
    
    None
}

/// Result of parsing a file
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ParseResult {
    pub units: Vec<TranslatableUnit>,
    pub file_type: String,
    pub encoding: String,
    pub line_count: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<serde_json::Value>,
}

impl ParseResult {
    pub fn new(file_type: impl Into<String>, encoding: impl Into<String>, line_count: u32) -> Self {
        Self {
            units: Vec::new(),
            file_type: file_type.into(),
            encoding: encoding.into(),
            line_count,
            metadata: None,
        }
    }

    pub fn with_units(mut self, units: Vec<TranslatableUnit>) -> Self {
        self.units = units;
        self
    }

    pub fn with_metadata(mut self, metadata: serde_json::Value) -> Self {
        self.metadata = Some(metadata);
        self
    }

    pub fn add_unit(&mut self, unit: TranslatableUnit) {
        self.units.push(unit);
    }

    pub fn is_empty(&self) -> bool {
        self.units.is_empty()
    }

    pub fn len(&self) -> usize {
        self.units.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_unit_type_serialization() {
        let unit_type = UnitType::Comment;
        let json = serde_json::to_string(&unit_type).unwrap();
        assert_eq!(json, r#""comment""#);
    }

    #[test]
    fn test_translatable_unit_creation() {
        let unit = TranslatableUnit::new(
            "test content".to_string(),
            UnitType::Comment,
            10,
            5,
        )
        .with_context("test context".to_string())
        .with_priority(Priority::High);

        assert_eq!(unit.content, "test content");
        assert_eq!(unit.line_number, 10);
        assert_eq!(unit.column_number, 5);
        assert_eq!(unit.priority, Priority::High);
        assert!(unit.context.is_some());
    }

    #[test]
    fn test_parse_result() {
        let mut result = ParseResult::new("python", "utf-8", 100);
        
        let unit = TranslatableUnit::new(
            "test".to_string(),
            UnitType::Comment,
            1,
            1,
        );
        
        result.add_unit(unit);
        
        assert_eq!(result.len(), 1);
        assert!(!result.is_empty());
        assert_eq!(result.file_type, "python");
    }
}


