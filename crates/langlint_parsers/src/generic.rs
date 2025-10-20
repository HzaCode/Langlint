use anyhow::Result;
use langlint_core::{ParseResult, TranslatableUnit, UnitType, Priority};
use regex::Regex;

use crate::Parser;

/// Generic code parser for various programming languages
/// Supports: JavaScript, TypeScript, Go, Rust, Java, C/C++, R, and more
pub struct GenericCodeParser;

impl GenericCodeParser {
    pub fn new() -> Self {
        Self
    }

    /// Get comment patterns for different languages
    fn get_comment_patterns(&self, extension: &str) -> CommentStyle {
        match extension {
            ".js" | ".ts" | ".jsx" | ".tsx" | ".java" | ".c" | ".cpp" | ".h" | ".hpp" | 
            ".cs" | ".go" | ".rs" | ".swift" | ".kt" | ".scala" => {
                CommentStyle {
                    single_line: vec!["//"],
                    multi_line_start: Some("/*"),
                    multi_line_end: Some("*/"),
                }
            }
            ".r" | ".R" | ".sh" | ".bash" | ".py" => {
                CommentStyle {
                    single_line: vec!["#"],
                    multi_line_start: None,
                    multi_line_end: None,
                }
            }
            ".lua" | ".sql" => {
                CommentStyle {
                    single_line: vec!["--"],
                    multi_line_start: Some("/*"),
                    multi_line_end: Some("*/"),
                }
            }
            _ => {
                // Default to C-style comments
                CommentStyle {
                    single_line: vec!["//"],
                    multi_line_start: Some("/*"),
                    multi_line_end: Some("*/"),
                }
            }
        }
    }

    /// Check if text should be translated
    fn is_translatable(&self, text: &str) -> bool {
        let text = text.trim();
        
        // Skip empty or very short text
        if text.len() < 3 {
            return false;
        }

        // Skip URLs
        if text.contains("://") {
            return false;
        }

        // Skip text that's mostly code or symbols
        let alpha_count = text.chars().filter(|c| c.is_alphabetic()).count();
        if alpha_count < text.len() / 3 {
            return false;
        }

        // Skip common technical terms
        let technical_terms = [
            "TODO", "FIXME", "NOTE", "HACK", "XXX", "BUG",
            "DEPRECATED", "WARNING", "ERROR",
        ];
        
        if technical_terms.iter().any(|term| text.to_uppercase().contains(term)) && text.len() < 20 {
            return false;
        }

        true
    }
}

impl Default for GenericCodeParser {
    fn default() -> Self {
        Self::new()
    }
}

struct CommentStyle {
    single_line: Vec<&'static str>,
    multi_line_start: Option<&'static str>,
    multi_line_end: Option<&'static str>,
}

impl Parser for GenericCodeParser {
    fn name(&self) -> &'static str {
        "GenericCodeParser"
    }

    fn supported_extensions(&self) -> &'static [&'static str] {
        &[
            ".js", ".ts", ".jsx", ".tsx",  // JavaScript/TypeScript
            ".go",                           // Go
            ".rs",                           // Rust
            ".java",                         // Java
            ".c", ".cpp", ".h", ".hpp",     // C/C++
            ".cs",                           // C#
            ".php",                          // PHP
            ".rb",                           // Ruby
            ".sh", ".bash",                  // Shell
            ".sql",                          // SQL
            ".r", ".R",                      // R
            ".m",                            // MATLAB/Objective-C
            ".scala",                        // Scala
            ".kt",                           // Kotlin
            ".swift",                        // Swift
            ".dart",                         // Dart
            ".lua",                          // Lua
            ".vim",                          // Vim script
        ]
    }

    fn can_parse(&self, path: &str, _content: Option<&str>) -> bool {
        self.supported_extensions().iter().any(|ext| path.ends_with(ext))
    }

    fn extract_units(&self, content: &str, path: &str) -> Result<ParseResult> {
        let mut units = Vec::new();
        let lines: Vec<&str> = content.lines().collect();

        // Determine comment style based on file extension
        let extension = std::path::Path::new(path)
            .extension()
            .and_then(|e| e.to_str())
            .map(|e| format!(".{}", e))
            .unwrap_or_else(|| ".unknown".to_string());

        let comment_style = self.get_comment_patterns(&extension);

        let mut in_multi_line_comment = false;
        let mut multi_line_content = String::new();
        let mut multi_line_start = 0;

        for (i, line) in lines.iter().enumerate() {
            let line_num = (i + 1) as u32;

            // Handle multi-line comments
            if let Some(start_marker) = comment_style.multi_line_start {
                if let Some(end_marker) = comment_style.multi_line_end {
                    if !in_multi_line_comment && line.contains(start_marker) {
                        in_multi_line_comment = true;
                        multi_line_start = line_num;
                        multi_line_content.clear();

                        // Extract content after start marker
                        if let Some(start_pos) = line.find(start_marker) {
                            let after_start = &line[start_pos + start_marker.len()..];
                            
                            // Check if comment ends on same line
                            if let Some(end_pos) = after_start.find(end_marker) {
                                let comment_text = after_start[..end_pos].trim();
                                if self.is_translatable(comment_text) {
                                    let mut unit = TranslatableUnit::new(
                                        comment_text.to_string(),
                                        UnitType::Comment,
                                        line_num,
                                        1,
                                    )
                                    .with_context(format!("Multi-line comment at line {}", line_num))
                                    .with_priority(Priority::Medium);

                                    // Detect language
                                    unit.detect_language();

                                    units.push(unit);
                                }
                                in_multi_line_comment = false;
                            } else {
                                multi_line_content.push_str(after_start.trim());
                                multi_line_content.push(' ');
                            }
                        }
                    } else if in_multi_line_comment {
                        if let Some(end_pos) = line.find(end_marker) {
                            // End of multi-line comment
                            multi_line_content.push_str(line[..end_pos].trim());
                            
                            if self.is_translatable(&multi_line_content) {
                                let mut unit = TranslatableUnit::new(
                                    multi_line_content.trim().to_string(),
                                    UnitType::Comment,
                                    multi_line_start,
                                    1,
                                )
                                .with_context(format!("Multi-line comment at lines {}-{}", multi_line_start, line_num))
                                .with_priority(Priority::Medium);

                                // Detect language
                                unit.detect_language();

                                units.push(unit);
                            }
                            
                            in_multi_line_comment = false;
                            multi_line_content.clear();
                        } else {
                            multi_line_content.push_str(line.trim());
                            multi_line_content.push(' ');
                        }
                    }
                }
            }

            // Handle single-line comments
            if !in_multi_line_comment {
                for marker in &comment_style.single_line {
                    if let Some(pos) = line.find(marker) {
                        let comment_text = line[pos + marker.len()..].trim();
                        
                        if self.is_translatable(comment_text) {
                            let mut unit = TranslatableUnit::new(
                                comment_text.to_string(),
                                UnitType::Comment,
                                line_num,
                                (pos + 1) as u32,
                            )
                            .with_context(format!("Single-line comment at line {}", line_num))
                            .with_priority(Priority::Medium);

                            // Detect language
                            unit.detect_language();

                            units.push(unit);
                        }
                        break;
                    }
                }
            }
        }

        let line_count = lines.len() as u32;
        let result = ParseResult::new("generic_code", "utf-8", line_count)
            .with_units(units)
            .with_metadata(serde_json::json!({
                "parser": "GenericCodeParser",
                "version": "0.1.0",
                "file_path": path,
                "extension": extension,
            }));

        Ok(result)
    }

    fn reconstruct(&self, original: &str, units: &[TranslatableUnit], path: &str) -> Result<String> {
        let mut result = original.to_string();

        // Sort units by line number (reverse order for safe replacement)
        let mut sorted_units: Vec<_> = units.iter().collect();
        sorted_units.sort_by(|a, b| b.line_number.cmp(&a.line_number));

        // Determine comment style
        let extension = std::path::Path::new(path)
            .extension()
            .and_then(|e| e.to_str())
            .map(|e| format!(".{}", e))
            .unwrap_or_else(|| ".unknown".to_string());

        let comment_style = self.get_comment_patterns(&extension);
        let lines: Vec<&str> = original.lines().collect();

        for unit in sorted_units {
            let line_idx = (unit.line_number as usize).saturating_sub(1);
            if line_idx >= lines.len() {
                continue;
            }

            let line = lines[line_idx];

            // Try to find and replace comment
            for marker in &comment_style.single_line {
                if let Some(pos) = line.find(marker) {
                    let before_comment = &line[..pos];
                    let new_line = format!("{}{} {}", before_comment, marker, unit.content);
                    
                    let old_line_pattern = regex::escape(line);
                    if let Ok(re) = Regex::new(&old_line_pattern) {
                        result = re.replace(&result, new_line.as_str()).to_string();
                    }
                    break;
                }
            }
        }

        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generic_parser_supported_extensions() {
        let parser = GenericCodeParser::new();
        
        assert!(parser.can_parse("test.js", None));
        assert!(parser.can_parse("test.go", None));
        assert!(parser.can_parse("test.rs", None));
        assert!(parser.can_parse("test.r", None));
        assert!(!parser.can_parse("test.txt", None));
    }

    #[test]
    fn test_extract_javascript_comment() {
        let parser = GenericCodeParser::new();
        let content = r#"
// This is a comment
function foo() {
    return 42;
}
"#;
        
        let result = parser.extract_units(content, "test.js").unwrap();
        assert!(!result.units.is_empty());
        assert!(result.units[0].content.contains("This is a comment"));
    }

    #[test]
    fn test_extract_multiline_comment() {
        let parser = GenericCodeParser::new();
        let content = r#"
/* This is a 
   multi-line comment */
function foo() {
    return 42;
}
"#;
        
        let result = parser.extract_units(content, "test.js").unwrap();
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_is_translatable() {
        let parser = GenericCodeParser::new();
        
        assert!(parser.is_translatable("This is a normal comment"));
        assert!(!parser.is_translatable("TODO"));
        assert!(!parser.is_translatable("http://example.com"));
        assert!(!parser.is_translatable("a"));  // Too short
    }

    #[test]
    fn test_extract_go_comment() {
        let parser = GenericCodeParser::new();
        let content = r#"// Package comment
package main
func main() {
    // Function comment
    println("Hello")
}
"#;
        let result = parser.extract_units(content, "test.go").unwrap();
        assert_eq!(result.file_type, "generic_code");
        assert!(!result.units.is_empty());
    }

    #[test]
    fn test_extract_rust_comment() {
        let parser = GenericCodeParser::new();
        let content = r#"/// Documentation comment
fn foo() -> i32 {
    // Regular comment
    42
}
"#;
        let result = parser.extract_units(content, "test.rs").unwrap();
        assert_eq!(result.file_type, "generic_code");
    }

    #[test]
    fn test_extract_empty_file() {
        let parser = GenericCodeParser::new();
        let content = "";
        let result = parser.extract_units(content, "test.js").unwrap();
        assert!(result.units.is_empty());
    }

    #[test]
    fn test_c_style_comments() {
        let parser = GenericCodeParser::new();
        let content = r#"// C comment
int main() {
    /* Block comment */
    return 0;
}
"#;
        let result = parser.extract_units(content, "test.c").unwrap();
        assert_eq!(result.file_type, "generic_code");
    }

    #[test]
    fn test_shell_comments() {
        let parser = GenericCodeParser::new();
        let content = "#!/bin/bash\n# Shell comment\necho hello\n";
        let result = parser.extract_units(content, "test.sh").unwrap();
        assert_eq!(result.file_type, "generic_code");
    }

    #[test]
    fn test_line_count() {
        let parser = GenericCodeParser::new();
        let content = "line1\nline2\nline3\n";
        let result = parser.extract_units(content, "test.js").unwrap();
        assert_eq!(result.line_count, 3);
    }

    #[test]
    fn test_parser_name() {
        let parser = GenericCodeParser::new();
        assert_eq!(parser.name(), "GenericCodeParser");
    }

    #[test]
    fn test_reconstruct_simple() {
        let parser = GenericCodeParser::new();
        let original = "// Old\ncode();";
        let mut result = parser.extract_units(original, "test.js").unwrap();
        if let Some(unit) = result.units.first_mut() {
            unit.content = "New".to_string();
        }
        let reconstructed = parser.reconstruct(original, &result.units, "test.js").unwrap();
        assert!(reconstructed.contains("New"));
    }
}

