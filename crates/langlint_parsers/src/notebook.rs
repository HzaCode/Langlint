//! Jupyter Notebook parser (.ipynb files)

use anyhow::Result;
use langlint_core::{ParseResult, Priority, TranslatableUnit, UnitType};
use regex::Regex;
use serde_json::Value;

use crate::Parser;

/// Parser for Jupyter Notebook files (.ipynb)
pub struct NotebookParser {
    comment_regex: Regex,
}

impl NotebookParser {
    /// Create a new notebook parser
    pub fn new() -> Self {
        Self {
            comment_regex: Regex::new(r"(?m)^\s*#\s*(.+)$").unwrap(),
        }
    }

    /// Extract translatable units from a notebook cell
    fn extract_from_cell(&self, cell: &Value, cell_index: usize) -> Vec<TranslatableUnit> {
        let mut units = Vec::new();

        let cell_type = cell["cell_type"].as_str().unwrap_or("");
        let source = match &cell["source"] {
            Value::Array(lines) => lines
                .iter()
                .filter_map(|v| v.as_str())
                .collect::<Vec<_>>()
                .join(""),
            Value::String(s) => s.clone(),
            _ => return units,
        };

        match cell_type {
            "markdown" => {
                // Extract text from markdown cells (excluding code blocks)
                if !source.trim().is_empty() && !source.starts_with("```") {
                    let priority = if source.starts_with('#') {
                        Priority::High // Headers
                    } else {
                        Priority::Medium
                    };

                    units.push(
                        TranslatableUnit::new(
                            source.trim().to_string(),
                            UnitType::TextNode,
                            cell_index as u32,
                            0,
                        )
                        .with_priority(priority),
                    );
                }
            }
            "code" => {
                // Extract comments from code cells
                for (line_num, line) in source.lines().enumerate() {
                    if let Some(captures) = self.comment_regex.captures(line) {
                        if let Some(comment) = captures.get(1) {
                            let comment_text = comment.as_str().trim();
                            if self.is_translatable(comment_text) {
                                units.push(
                                    TranslatableUnit::new(
                                        comment_text.to_string(),
                                        UnitType::Comment,
                                        (cell_index * 1000 + line_num) as u32,
                                        0,
                                    )
                                    .with_priority(Priority::Medium),
                                );
                            }
                        }
                    }
                }
            }
            _ => {}
        }

        units
    }

    /// Check if text is translatable (not code, URL, etc.)
    fn is_translatable(&self, text: &str) -> bool {
        // Skip short texts
        if text.len() < 3 {
            return false;
        }

        // Skip if it looks like code
        if text.contains("import ")
            || text.contains("def ")
            || text.contains("class ")
            || text.contains("return ")
            || text.contains("=")
            || text.contains("{")
            || text.contains("}")
        {
            return false;
        }

        // Skip URLs
        if text.contains("http://") || text.contains("https://") {
            return false;
        }

        // Skip if mostly non-alphabetic
        let alpha_count = text.chars().filter(|c| c.is_alphabetic()).count();
        if alpha_count < text.len() / 2 {
            return false;
        }

        // Only translate text containing non-ASCII (non-English) characters
        if !self.contains_non_ascii(text) {
            return false;
        }

        true
    }

    /// Check if text contains non-ASCII characters
    fn contains_non_ascii(&self, text: &str) -> bool {
        text.chars().any(|c| c as u32 > 127)
    }
}

impl Default for NotebookParser {
    fn default() -> Self {
        Self::new()
    }
}

impl Parser for NotebookParser {
    fn name(&self) -> &'static str {
        "Notebook"
    }

    fn supported_extensions(&self) -> &'static [&'static str] {
        &[".ipynb"]
    }

    fn can_parse(&self, path: &str, _content: Option<&str>) -> bool {
        path.ends_with(".ipynb")
    }

    fn extract_units(&self, content: &str, _path: &str) -> Result<ParseResult> {
        // Parse JSON
        let notebook: Value = serde_json::from_str(content)?;

        let mut all_units = Vec::new();

        // Extract from cells
        if let Some(cells) = notebook["cells"].as_array() {
            for (index, cell) in cells.iter().enumerate() {
                let units = self.extract_from_cell(cell, index);
                all_units.extend(units);
            }
        }

        let line_count = content.lines().count() as u32;

        Ok(ParseResult {
            units: all_units,
            file_type: "jupyter_notebook".to_string(),
            encoding: "utf-8".to_string(),
            line_count,
            metadata: None,
        })
    }

    fn reconstruct(
        &self,
        original: &str,
        units: &[TranslatableUnit],
        _path: &str,
    ) -> Result<String> {
        // Parse original notebook
        let mut notebook: Value = serde_json::from_str(original)?;

        // Create a map of original text to translated text
        let mut translations = std::collections::HashMap::new();
        for unit in units {
            translations.insert(unit.content.clone(), unit.content.clone());
        }

        // Replace content in cells
        if let Some(cells) = notebook["cells"].as_array_mut() {
            for cell in cells.iter_mut() {
                // Get the source as string to check translations
                let source_text = match &cell["source"] {
                    Value::Array(lines) => lines
                        .iter()
                        .filter_map(|v| v.as_str())
                        .collect::<Vec<_>>()
                        .join(""),
                    Value::String(s) => s.clone(),
                    _ => continue,
                };

                // Check if we have a translation for this content
                if let Some(translated) = translations.get(source_text.trim()) {
                    cell["source"] = Value::String(translated.clone());
                }
            }
        }

        // Serialize back to JSON
        Ok(serde_json::to_string_pretty(&notebook)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_notebook_parser_can_parse() {
        let parser = NotebookParser::new();
        assert!(parser.can_parse("test.ipynb", None));
        assert!(!parser.can_parse("test.py", None));
    }

    #[test]
    fn test_notebook_parser_extract() {
        let parser = NotebookParser::new();
        let notebook_json = "{\"cells\":[{\"cell_type\":\"markdown\",\"source\":[\"# Test\"]},{\"cell_type\":\"code\",\"source\":[\"# Comment\"]}]}";

        let result = parser.extract_units(notebook_json, "test.ipynb").unwrap();
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_is_translatable() {
        let parser = NotebookParser::new();
        assert!(parser.is_translatable("This is a comment"));
        assert!(!parser.is_translatable("import numpy as np"));
        assert!(!parser.is_translatable("x = 5"));
        assert!(!parser.is_translatable("https://example.com"));
    }

    #[test]
    fn test_parser_name() {
        let parser = NotebookParser::new();
        assert_eq!(parser.name(), "Notebook");
    }

    #[test]
    fn test_extract_markdown_cell() {
        let parser = NotebookParser::new();
        let notebook_json =
            r#"{"cells":[{"cell_type":"markdown","source":["This is markdown text content"]}]}"#;
        let result = parser.extract_units(notebook_json, "test.ipynb").unwrap();
        assert_eq!(result.file_type, "jupyter_notebook");
    }

    #[test]
    fn test_extract_code_comment() {
        let parser = NotebookParser::new();
        let notebook_json = "{\"cells\":[{\"cell_type\":\"code\",\"source\":[\"# comment\"]}]}";
        let result = parser.extract_units(notebook_json, "test.ipynb").unwrap();
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_extract_empty_notebook() {
        let parser = NotebookParser::new();
        let notebook_json = r#"{"cells": []}"#;
        let result = parser.extract_units(notebook_json, "test.ipynb").unwrap();
        assert!(result.units.is_empty());
    }

    #[test]
    fn test_extract_mixed_cells() {
        let parser = NotebookParser::new();
        let notebook_json = "{\"cells\":[{\"cell_type\":\"markdown\",\"source\":[\"text\"]},{\"cell_type\":\"code\",\"source\":[\"// comment\"]}]}";
        let result = parser.extract_units(notebook_json, "test.ipynb").unwrap();
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_extract_multiline_source() {
        let parser = NotebookParser::new();
        let notebook_json = "{\"cells\":[{\"cell_type\":\"code\",\"source\":[\"# comment\"]}]}";
        let result = parser.extract_units(notebook_json, "test.ipynb").unwrap();
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_invalid_json() {
        let parser = NotebookParser::new();
        let invalid_json = "not valid json";
        let result = parser.extract_units(invalid_json, "test.ipynb");
        assert!(result.is_err());
    }
}
