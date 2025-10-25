use anyhow::Result;
use langlint_core::{ParseResult, TranslatableUnit, UnitType, Priority};
use regex::Regex;
use std::sync::OnceLock;

use crate::Parser;

/// Python parser for extracting comments and docstrings
pub struct PythonParser;

impl PythonParser {
    pub fn new() -> Self {
        Self
    }

    /// Check if text should be translated
    fn is_translatable(&self, text: &str) -> bool {
        let text = text.trim();
        
        // Skip empty or very short text
        if text.len() < 3 {
            return false;
        }

        // Skip URLs and emails
        if text.contains("://") || text.contains('@') && text.contains('.') {
            return false;
        }

        // Skip text that's mostly code or symbols
        // Count alphabetic chars AND CJK characters (Chinese, Japanese, Korean)
        let char_count = text.chars().count();
        let meaningful_count = text.chars().filter(|c| {
            c.is_alphabetic() || 
            ('\u{4E00}'..='\u{9FFF}').contains(c) ||  // CJK Unified Ideographs
            ('\u{3400}'..='\u{4DBF}').contains(c) ||  // CJK Extension A
            ('\u{3040}'..='\u{30FF}').contains(c) ||  // Hiragana + Katakana
            ('\u{AC00}'..='\u{D7AF}').contains(c)     // Hangul
        }).count();
        
        if meaningful_count < char_count / 3 {
            return false;
        }

        // Skip common technical terms
        let technical_terms = [
            "TODO", "FIXME", "NOTE", "HACK", "XXX",
            "self", "cls", "args", "kwargs",
            "return", "def", "class", "import",
        ];
        
        if technical_terms.contains(&text) {
            return false;
        }

        true
    }
}

impl Default for PythonParser {
    fn default() -> Self {
        Self::new()
    }
}

impl Parser for PythonParser {
    fn name(&self) -> &'static str {
        "PythonParser"
    }

    fn supported_extensions(&self) -> &'static [&'static str] {
        &[".py", ".pyi", ".pyw"]
    }

    fn can_parse(&self, path: &str, content: Option<&str>) -> bool {
        // Check extension
        if self.supported_extensions().iter().any(|ext| path.ends_with(ext)) {
            return true;
        }

        // Check content for Python patterns
        if let Some(content) = content {
            let sample = &content[..content.len().min(500)];
            sample.contains("def ") || sample.contains("class ") || sample.contains("import ")
        } else {
            false
        }
    }

    fn extract_units(&self, content: &str, path: &str) -> Result<ParseResult> {
        let mut units = Vec::new();
        let lines: Vec<&str> = content.lines().collect();

        // Regex for single-line comments
        static COMMENT_RE: OnceLock<Regex> = OnceLock::new();
        let comment_re = COMMENT_RE.get_or_init(|| Regex::new(r"^\s*#\s*(.+)$").unwrap());

        // Regex for docstrings (simplified)
        static DOCSTRING_RE: OnceLock<Regex> = OnceLock::new();
        let docstring_re = DOCSTRING_RE.get_or_init(|| {
            Regex::new(r#"^\s*["']{3}(.+?)["']{3}"#).unwrap()
        });
        
        // Regex for multi-line docstring start
        static DOCSTRING_START_RE: OnceLock<Regex> = OnceLock::new();
        let docstring_start_re = DOCSTRING_START_RE.get_or_init(|| {
            Regex::new(r#"^\s*(["']{3})\s*(.*)$"#).unwrap()
        });

        let mut i = 0;
        while i < lines.len() {
            let line_num = (i + 1) as u32;
            let line = lines[i];

            // Extract single-line comments
            if let Some(caps) = comment_re.captures(line) {
                if let Some(comment_text) = caps.get(1) {
                    let text = comment_text.as_str().trim();
                    if self.is_translatable(text) {
                        let mut unit = TranslatableUnit::new(
                            text.to_string(),
                            UnitType::Comment,
                            line_num,
                            1,
                        )
                        .with_context(format!("Line {}: {}", line_num, line.trim()))
                        .with_priority(Priority::Medium);

                        // Detect language
                        unit.detect_language();

                        units.push(unit);
                    }
                }
            }

            // Extract single-line docstrings
            if let Some(caps) = docstring_re.captures(line) {
                if let Some(docstring_text) = caps.get(1) {
                    let text = docstring_text.as_str().trim();
                    if self.is_translatable(text) {
                        let mut unit = TranslatableUnit::new(
                            text.to_string(),
                            UnitType::Docstring,
                            line_num,
                            1,
                        )
                        .with_context(format!("Docstring at line {}", line_num))
                        .with_priority(Priority::High);

                        // Detect language
                        unit.detect_language();

                        units.push(unit);
                    }
                }
                i += 1;
                continue;
            }
            
            // Extract multi-line docstrings
            if let Some(caps) = docstring_start_re.captures(line) {
                let quote = caps.get(1).unwrap().as_str();
                let first_line_content = caps.get(2).map(|m| m.as_str().trim()).unwrap_or("");
                
                // Check if it's actually a single-line docstring (ends on same line)
                if !first_line_content.is_empty() && line.trim_end().ends_with(quote) {
                    i += 1;
                    continue;
                }
                
                // Multi-line docstring
                let start_line = line_num;
                let mut docstring_lines = Vec::new();
                
                if !first_line_content.is_empty() {
                    docstring_lines.push(first_line_content.to_string());
                }
                
                i += 1;
                let mut found_end = false;
                let mut end_line = start_line;
                
                while i < lines.len() {
                    let current_line = lines[i];
                    end_line = (i + 1) as u32;
                    
                    if current_line.contains(quote) {
                        // Found closing quotes
                        if let Some(end_pos) = current_line.find(quote) {
                            let last_content = current_line[..end_pos].trim();
                            if !last_content.is_empty() {
                                docstring_lines.push(last_content.to_string());
                            }
                        }
                        found_end = true;
                        break;
                    } else {
                        // Middle line of docstring
                        let content = current_line.trim();
                        if !content.is_empty() {
                            docstring_lines.push(content.to_string());
                        }
                    }
                    i += 1;
                }
                
                if found_end {
                    let docstring_content = docstring_lines.join(" ");
                    if self.is_translatable(&docstring_content) {
                        let span = end_line - start_line + 1;
                        let mut unit = TranslatableUnit::new(
                            docstring_content,
                            UnitType::Docstring,
                            start_line,
                            1,  // column
                        )
                        .with_metadata(serde_json::json!({"span": span, "end_line": end_line}))
                        .with_context(format!("Multi-line docstring at lines {}-{}", start_line, end_line))
                        .with_priority(Priority::High);

                        // Detect language
                        unit.detect_language();

                        units.push(unit);
                    }
                }
            }

            i += 1;
        }

        let line_count = lines.len() as u32;
        let result = ParseResult::new("python", "utf-8", line_count)
            .with_units(units)
            .with_metadata(serde_json::json!({
                "parser": "PythonParser",
                "version": "0.1.0",
                "file_path": path,
            }));

        Ok(result)
    }

    fn reconstruct(&self, original: &str, units: &[TranslatableUnit], _path: &str) -> Result<String> {
        // Build a map of line numbers to translated content
        let mut line_replacements: std::collections::HashMap<u32, String> = std::collections::HashMap::new();
        let mut lines_to_skip: std::collections::HashSet<u32> = std::collections::HashSet::new();
        
        let lines: Vec<&str> = original.lines().collect();

        for unit in units {
            let line_idx = (unit.line_number as usize).saturating_sub(1);
            if line_idx >= lines.len() {
                continue;
            }

            let line = lines[line_idx];

            // Replace comments (single line)
            if unit.unit_type == UnitType::Comment {
                if let Some(hash_pos) = line.find('#') {
                    let before_comment = &line[..hash_pos];
                    let new_line = format!("{}# {}", before_comment, unit.content);
                    line_replacements.insert(unit.line_number, new_line);
                }
            }
            // Replace docstrings
            else if unit.unit_type == UnitType::Docstring {
                let quote_style = if line.contains(r#"""""#) { r#"""""# } else { "'''" };
                let indent = line.chars().take_while(|c| c.is_whitespace()).collect::<String>();
                
                // Check if it's multi-line (has span metadata)
                let span = unit.metadata.as_ref()
                    .and_then(|m| m.get("span"))
                    .and_then(|s| s.as_u64())
                    .unwrap_or(1) as u32;
                
                if span == 1 {
                    // Single-line docstring
                    let new_line = format!("{}{}{}{}", indent, quote_style, unit.content, quote_style);
                    line_replacements.insert(unit.line_number, new_line);
                } else {
                    // Multi-line docstring: collapse to single line
                    let new_line = format!("{}{}{}{}", indent, quote_style, unit.content, quote_style);
                    line_replacements.insert(unit.line_number, new_line);
                    
                    // Mark other lines for skipping
                    for offset in 1..span {
                        lines_to_skip.insert(unit.line_number + offset);
                    }
                }
            }
        }

        // Reconstruct file line by line
        let mut result_lines = Vec::new();
        for (i, line) in lines.iter().enumerate() {
            let line_num = (i + 1) as u32;
            
            if lines_to_skip.contains(&line_num) {
                // Skip this line (part of multi-line docstring)
                continue;
            }
            
            if let Some(new_line) = line_replacements.get(&line_num) {
                result_lines.push(new_line.as_str());
            } else {
                result_lines.push(line);
            }
        }

        Ok(result_lines.join("\n"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_python_parser_new() {
        let parser = PythonParser::new();
        assert_eq!(parser.name(), "PythonParser");
    }

    #[test]
    fn test_python_parser_default() {
        let parser = PythonParser;
        assert_eq!(parser.name(), "PythonParser");
    }

    #[test]
    fn test_supported_extensions() {
        let parser = PythonParser::new();
        let extensions = parser.supported_extensions();
        
        assert!(extensions.contains(&".py"));
        assert!(extensions.contains(&".pyi"));
        assert!(extensions.contains(&".pyw"));
    }

    #[test]
    fn test_python_parser_can_parse() {
        let parser = PythonParser::new();
        
        assert!(parser.can_parse("test.py", None));
        assert!(parser.can_parse("test.pyi", None));
        assert!(parser.can_parse("test.pyw", None));
        assert!(!parser.can_parse("test.txt", None));
        assert!(!parser.can_parse("test.js", None));
        
        let python_content = "def foo():\n    pass";
        assert!(parser.can_parse("unknown", Some(python_content)));
        
        let python_with_class = "class MyClass:\n    pass";
        assert!(parser.can_parse("unknown", Some(python_with_class)));
        
        let python_with_import = "import os\nimport sys";
        assert!(parser.can_parse("unknown", Some(python_with_import)));
    }

    #[test]
    fn test_can_parse_non_python_content() {
        let parser = PythonParser::new();
        let non_python = "This is just plain text without Python syntax";
        
        assert!(!parser.can_parse("unknown.txt", Some(non_python)));
    }

    #[test]
    fn test_extract_comment() {
        let parser = PythonParser::new();
        let content = r#"
# This is a comment
def foo():
    pass
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert!(!result.units.is_empty());
        assert!(result.units[0].content.contains("This is a comment"));
        assert_eq!(result.units[0].unit_type, UnitType::Comment);
        assert_eq!(result.units[0].line_number, 2);
    }

    #[test]
    fn test_extract_multiple_comments() {
        let parser = PythonParser::new();
        let content = r#"
# Comment 1
def foo():
    # Comment 2
    pass
# Comment 3
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert_eq!(result.units.len(), 3);
    }

    #[test]
    fn test_extract_docstring() {
        let parser = PythonParser::new();
        let content = r#"
def foo():
    """This is a docstring"""
    pass
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert!(!result.units.is_empty());
        assert_eq!(result.units[0].unit_type, UnitType::Docstring);
        assert_eq!(result.units[0].priority, Priority::High);
    }

    #[test]
    fn test_extract_single_quote_docstring() {
        let parser = PythonParser::new();
        let content = r#"
def foo():
    '''This is a docstring with single quotes'''
    pass
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_extract_empty_file() {
        let parser = PythonParser::new();
        let content = "";
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert!(result.units.is_empty());
    }

    #[test]
    fn test_extract_no_translatable() {
        let parser = PythonParser::new();
        let content = r#"
# TODO
# FIXME
def foo():
    pass
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        // TODO and FIXME should be filtered out
        assert!(result.units.is_empty());
    }

    #[test]
    fn test_is_translatable() {
        let parser = PythonParser::new();
        
        // Should be translatable
        assert!(parser.is_translatable("This is a normal comment"));
        assert!(parser.is_translatable("Calculate the sum of numbers"));
        assert!(parser.is_translatable("   Text with spaces   "));
        
        // Should not be translatable
        assert!(!parser.is_translatable("TODO"));
        assert!(!parser.is_translatable("FIXME"));
        assert!(!parser.is_translatable("NOTE"));
        assert!(!parser.is_translatable("http://example.com"));
        assert!(!parser.is_translatable("user@example.com"));
        assert!(!parser.is_translatable("a"));  // Too short
        assert!(!parser.is_translatable("ab")); // Too short
        assert!(!parser.is_translatable(""));   // Empty
        assert!(!parser.is_translatable("   ")); // Whitespace only
        assert!(!parser.is_translatable("!!!"));  // Mostly symbols
        assert!(!parser.is_translatable("self"));
        assert!(!parser.is_translatable("cls"));
        assert!(!parser.is_translatable("args"));
        assert!(!parser.is_translatable("kwargs"));
    }

    #[test]
    fn test_is_translatable_with_url() {
        let parser = PythonParser::new();
        
        assert!(!parser.is_translatable("See https://example.com for details"));
        assert!(!parser.is_translatable("Contact us at support@example.com"));
    }

    #[test]
    fn test_is_translatable_mostly_symbols() {
        let parser = PythonParser::new();
        
        // Text with too many symbols should not be translatable
        assert!(!parser.is_translatable("========"));
        assert!(!parser.is_translatable("--------"));
        assert!(!parser.is_translatable("########"));
    }

    #[test]
    fn test_reconstruct_comment() {
        let parser = PythonParser::new();
        let original = "# Original comment\ndef foo():\n    pass";
        
        let translated_unit = TranslatableUnit::new(
            "Translated comment".to_string(),
            UnitType::Comment,
            1,
            1,
        );
        
        let result = parser.reconstruct(original, &[translated_unit], "test.py").unwrap();
        assert!(result.contains("Translated comment"));
        assert!(result.contains("def foo()"));
    }

    #[test]
    fn test_reconstruct_docstring() {
        let parser = PythonParser::new();
        let original = r#"def foo():
    """Original docstring"""
    pass"#;
        
        let translated_unit = TranslatableUnit::new(
            "Translated docstring".to_string(),
            UnitType::Docstring,
            2,
            1,
        );
        
        let result = parser.reconstruct(original, &[translated_unit], "test.py").unwrap();
        assert!(result.contains("Translated docstring"));
    }

    #[test]
    fn test_reconstruct_empty_units() {
        let parser = PythonParser::new();
        let original = "def foo():\n    pass";
        
        let result = parser.reconstruct(original, &[], "test.py").unwrap();
        assert_eq!(result, original);
    }

    #[test]
    fn test_extract_with_metadata() {
        let parser = PythonParser::new();
        let content = "# Test comment\ndef foo():\n    pass";
        
        let result = parser.extract_units(content, "test.py").unwrap();
        
        assert_eq!(result.file_type, "python");
        assert_eq!(result.encoding, "utf-8");
        assert!(result.line_count > 0);
        assert!(result.metadata.is_some());
    }

    #[test]
    fn test_extract_indented_comment() {
        let parser = PythonParser::new();
        let content = r#"
def foo():
    # Indented comment
    pass
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert!(!result.units.is_empty());
        assert!(result.units[0].content.contains("Indented comment"));
    }

    #[test]
    fn test_parser_name() {
        let parser = PythonParser::new();
        assert_eq!(parser.name(), "PythonParser");
    }

    #[test]
    fn test_extract_units_context() {
        let parser = PythonParser::new();
        let content = "# Test comment\nprint('hello')";
        
        let result = parser.extract_units(content, "test.py").unwrap();
        assert!(!result.units.is_empty());
        assert!(result.units[0].context.is_some());
    }

    #[test]
    fn test_extract_units_priority() {
        let parser = PythonParser::new();
        let content = r#"
# Comment with medium priority
def foo():
    """Docstring with high priority"""
    pass
"#;
        
        let result = parser.extract_units(content, "test.py").unwrap();
        
        // Find comment and docstring
        let comment = result.units.iter().find(|u| u.unit_type == UnitType::Comment);
        let docstring = result.units.iter().find(|u| u.unit_type == UnitType::Docstring);
        
        if let Some(c) = comment {
            assert_eq!(c.priority, Priority::Medium);
        }
        
        if let Some(d) = docstring {
            assert_eq!(d.priority, Priority::High);
        }
    }
}

