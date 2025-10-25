use anyhow::Result;
use langlint_core::{ParseResult, TranslatableUnit};

/// Parser trait that all file type parsers must implement
pub trait Parser: Send + Sync {
    /// Get the name of this parser
    fn name(&self) -> &'static str;

    /// Get the list of file extensions this parser supports
    fn supported_extensions(&self) -> &'static [&'static str];

    /// Check if this parser can handle the given file
    ///
    /// # Arguments
    /// * `path` - The file path
    /// * `content` - Optional file content for content-based detection
    fn can_parse(&self, path: &str, content: Option<&str>) -> bool;

    /// Extract translatable units from file content
    ///
    /// # Arguments
    /// * `content` - The file content to parse
    /// * `path` - The file path (for context/metadata)
    fn extract_units(&self, content: &str, path: &str) -> Result<ParseResult>;

    /// Reconstruct file content with translated units
    ///
    /// # Arguments
    /// * `original` - The original file content
    /// * `units` - The translated units
    /// * `path` - The file path (for context)
    fn reconstruct(&self, original: &str, units: &[TranslatableUnit], path: &str)
        -> Result<String>;
}

pub mod generic;
pub mod notebook;
pub mod python;

// Re-export parsers
pub use generic::GenericCodeParser;
pub use notebook::NotebookParser;
pub use python::PythonParser;
