//! Python bindings for langlint using PyO3
//!
//! This module provides Python bindings for the Rust implementation of langlint.
//! All core functionality is implemented in Rust for maximum performance.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use langlint_core::ParseResult;
use langlint_parsers::{GenericCodeParser, Parser, PythonParser};
use langlint_translators::{GoogleTranslator, MockTranslator, Translator};

use std::fs;
use std::path::Path;
use walkdir::WalkDir;

/// Scan files and extract translatable units
///
/// Args:
///     path: File or directory path to scan
///     format: Output format ('json' or 'text'), defaults to 'json'
///     verbose: Enable verbose output, defaults to False
///     exclude: List of patterns to exclude (e.g., ['demo_files', 'examples'])
///
/// Returns:
///     JSON string with scan results
#[pyfunction]
#[pyo3(signature = (path, format=None, verbose=None, exclude=None))]
fn scan(
    path: String,
    format: Option<String>,
    verbose: Option<bool>,
    exclude: Option<Vec<String>>,
) -> PyResult<String> {
    let format = format.unwrap_or_else(|| "json".to_string());
    let verbose = verbose.unwrap_or(false);
    let exclude = exclude.unwrap_or_default();

    // Run the scan in a tokio runtime
    let result = tokio::runtime::Runtime::new()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?
        .block_on(async { scan_impl(&path, &format, verbose, &exclude).await });

    result.map_err(|e| PyRuntimeError::new_err(format!("Scan failed: {}", e)))
}

/// Implementation of scan functionality
async fn scan_impl(
    path: &str,
    format: &str,
    verbose: bool,
    exclude: &[String],
) -> anyhow::Result<String> {
    let path_obj = Path::new(path);

    // Collect files to scan
    let files = if path_obj.is_file() {
        vec![path_obj.to_path_buf()]
    } else {
        collect_files(path_obj, exclude)?
    };

    if verbose {
        eprintln!("Scanning {} files...", files.len());
    }

    // Scan all files with their paths
    let mut all_results = Vec::new();
    let mut total_units = 0;

    for file_path in &files {
        if let Ok(result) = scan_file(file_path).await {
            total_units += result.units.len();
            all_results.push((file_path.clone(), result));
        }
    }

    // Format output
    if format == "json" {
        let output = serde_json::json!({
            "files_scanned": files.len(),
            "total_units": total_units,
            "results": all_results.iter().map(|(path, r)| {
                serde_json::json!({
                    "file": path.display().to_string(),
                    "units": r.units.len(),
                })
            }).collect::<Vec<_>>()
        });
        Ok(serde_json::to_string_pretty(&output)?)
    } else {
        Ok(format!(
            "Scanned {} files, found {} translatable units",
            files.len(),
            total_units
        ))
    }
}

/// Translate files from source to target language
///
/// Args:
///     path: File or directory path to translate
///     source: Source language code (e.g., 'en', 'zh', 'ja')
///     target: Target language code (e.g., 'en', 'zh', 'ja')
///     translator: Translator to use ('mock', 'google'), defaults to 'google'
///     output: Output file path (optional, defaults to in-place)
///     dry_run: Perform dry run without writing, defaults to False
///
/// Returns:
///     JSON string with translation results
#[pyfunction]
#[pyo3(signature = (path, source, target, translator=None, output=None, dry_run=None))]
fn translate(
    path: String,
    source: String,
    target: String,
    translator: Option<String>,
    output: Option<String>,
    dry_run: Option<bool>,
) -> PyResult<String> {
    let translator = translator.unwrap_or_else(|| "google".to_string());
    let dry_run = dry_run.unwrap_or(false);

    // Run the translation in a tokio runtime
    let result = tokio::runtime::Runtime::new()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?
        .block_on(async {
            translate_impl(
                &path,
                &source,
                &target,
                &translator,
                output.as_deref(),
                dry_run,
            )
            .await
        });

    result.map_err(|e| PyRuntimeError::new_err(format!("Translation failed: {}", e)))
}

/// Implementation of translate functionality
async fn translate_impl(
    path: &str,
    source: &str,
    target: &str,
    translator_name: &str,
    output: Option<&str>,
    dry_run: bool,
) -> anyhow::Result<String> {
    let path_obj = Path::new(path);

    // Create translator
    let translator: Box<dyn Translator> = match translator_name {
        "google" => Box::new(GoogleTranslator::new()?),
        _ => Box::new(MockTranslator::default()),
    };

    // Scan file first
    let parse_result = scan_file(path_obj).await?;

    if parse_result.units.is_empty() {
        return Ok(serde_json::json!({
            "status": "success",
            "translated": 0,
            "message": "No translatable units found"
        })
        .to_string());
    }

    // Translate all units
    let texts: Vec<String> = parse_result
        .units
        .iter()
        .map(|u| u.content.clone())
        .collect();

    let translations = translator.translate_batch(&texts, source, target).await?;

    // Create new units with translations
    let mut translated_units = parse_result.units.clone();
    for (i, trans) in translations.iter().enumerate() {
        if i < translated_units.len() {
            translated_units[i].content = trans.translated_text.clone();
        }
    }

    // Write output (if not dry run)
    if !dry_run {
        let output_path = output.unwrap_or(path);

        // Create backup
        if output.is_none() {
            let backup_path = format!("{}.backup", path);
            fs::copy(path, &backup_path)?;
        }

        // Reconstruct file
        let original_content = fs::read_to_string(path)?;
        let parser = get_parser(path_obj);
        let reconstructed = parser.reconstruct(&original_content, &translated_units, path)?;

        fs::write(output_path, reconstructed)?;
    }

    Ok(serde_json::json!({
        "status": "success",
        "translated": translations.len(),
        "dry_run": dry_run,
        "output": output.unwrap_or(path)
    })
    .to_string())
}

/// Get version string
#[pyfunction]
fn version() -> PyResult<String> {
    Ok(env!("CARGO_PKG_VERSION").to_string())
}

/// Python module definition
#[pymodule]
fn langlint_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scan, m)?)?;
    m.add_function(wrap_pyfunction!(translate, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    Ok(())
}

// ============================================================================
// Helper functions
// ============================================================================

/// Collect files to scan from a directory
fn collect_files(dir: &Path, exclude: &[String]) -> anyhow::Result<Vec<std::path::PathBuf>> {
    let mut files = Vec::new();

    for entry in WalkDir::new(dir)
        .follow_links(true)
        .into_iter()
        .filter_entry(|e| !is_ignored(e.path(), exclude))
    {
        let entry = entry?;
        if entry.file_type().is_file() {
            let path = entry.path();
            if should_scan(path) {
                files.push(path.to_path_buf());
            }
        }
    }

    Ok(files)
}

/// Check if a path should be ignored
fn is_ignored(path: &Path, exclude_patterns: &[String]) -> bool {
    // Default ignored directories
    let default_ignored_dirs = [
        "node_modules",
        "target",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "build",
        "dist",
        ".eggs",
        "htmlcov",
        "demo_files",
        "examples",
        "figures",
        "submission_patterns",
    ];

    // Check default ignored directories
    let is_default_ignored = path.components().any(|c| {
        if let Some(s) = c.as_os_str().to_str() {
            default_ignored_dirs.contains(&s)
        } else {
            false
        }
    });

    if is_default_ignored {
        return true;
    }

    // Check custom exclude patterns
    if !exclude_patterns.is_empty() {
        let path_str = path.to_string_lossy();
        for pattern in exclude_patterns {
            if path_str.contains(pattern.as_str()) {
                return true;
            }
        }
    }

    false
}

/// Check if a file should be scanned
fn should_scan(path: &Path) -> bool {
    if let Some(ext) = path.extension() {
        let ext_str = ext.to_string_lossy();
        matches!(
            ext_str.as_ref(),
            "py" | "js"
                | "ts"
                | "jsx"
                | "tsx"
                | "rs"
                | "go"
                | "java"
                | "c"
                | "cpp"
                | "h"
                | "hpp"
                | "cs"
                | "php"
                | "rb"
                | "sh"
                | "bash"
                | "sql"
                | "r"
                | "R"
                | "m"
                | "scala"
                | "kt"
                | "swift"
                | "dart"
                | "lua"
                | "vim"
                | "ipynb"
        )
    } else {
        false
    }
}

/// Scan a single file
async fn scan_file(path: &Path) -> anyhow::Result<ParseResult> {
    let content = fs::read_to_string(path)?;
    let path_str = path.to_string_lossy();

    let parser = get_parser(path);
    parser.extract_units(&content, &path_str)
}

/// Get appropriate parser for a file
fn get_parser(path: &Path) -> Box<dyn Parser> {
    let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");

    match ext {
        "py" => Box::new(PythonParser),
        _ => Box::new(GenericCodeParser),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_module_creation() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::new(py, "langlint_py").unwrap();
            assert!(module.name().unwrap() == "langlint_py");
        });
    }

    #[test]
    fn test_is_ignored_default_dirs() {
        // Test default ignored directories
        assert!(is_ignored(Path::new("node_modules/test.js"), &[]));
        assert!(is_ignored(Path::new("target/debug/test"), &[]));
        assert!(is_ignored(Path::new("__pycache__/test.pyc"), &[]));
        assert!(is_ignored(Path::new(".git/config"), &[]));
        assert!(is_ignored(Path::new("demo_files/test.py"), &[]));
        assert!(is_ignored(Path::new("examples/test.py"), &[]));
        assert!(is_ignored(Path::new("figures/test.png"), &[]));
        assert!(is_ignored(Path::new("submission_patterns/test.md"), &[]));

        // Test non-ignored directories
        assert!(!is_ignored(Path::new("src/main.rs"), &[]));
        assert!(!is_ignored(Path::new("tests/test.py"), &[]));
    }

    #[test]
    fn test_is_ignored_custom_patterns() {
        let exclude = vec!["custom_dir".to_string(), "temp".to_string()];

        // Test custom patterns
        assert!(is_ignored(Path::new("custom_dir/test.py"), &exclude));
        assert!(is_ignored(Path::new("temp/data.txt"), &exclude));
        assert!(is_ignored(Path::new("path/to/temp/file.rs"), &exclude));

        // Test non-matching paths
        assert!(!is_ignored(Path::new("src/main.rs"), &exclude));
    }

    #[test]
    fn test_is_ignored_combined() {
        let exclude = vec!["my_tests".to_string()];

        // Both default and custom should work
        assert!(is_ignored(Path::new("node_modules/lib.js"), &exclude));
        assert!(is_ignored(Path::new("my_tests/test.py"), &exclude));
        assert!(is_ignored(Path::new("demo_files/example.py"), &exclude));
    }

    #[test]
    fn test_should_scan() {
        // Valid extensions
        assert!(should_scan(Path::new("test.py")));
        assert!(should_scan(Path::new("test.js")));
        assert!(should_scan(Path::new("test.rs")));
        assert!(should_scan(Path::new("test.ipynb")));

        // Invalid extensions
        assert!(!should_scan(Path::new("test.txt")));
        assert!(!should_scan(Path::new("test.md")));
        assert!(!should_scan(Path::new("README")));
    }

    #[test]
    fn test_collect_files_with_exclude() {
        use std::fs;
        use tempfile::TempDir;

        // Create temporary directory structure
        let temp_dir = TempDir::new().unwrap();
        let base_path = temp_dir.path();

        // Create test files
        fs::create_dir(base_path.join("src")).unwrap();
        fs::create_dir(base_path.join("demo_files")).unwrap();
        fs::write(base_path.join("src/main.py"), "# test").unwrap();
        fs::write(base_path.join("demo_files/demo.py"), "# demo").unwrap();

        // Collect without exclude
        let files_all = collect_files(base_path, &[]).unwrap();
        assert_eq!(files_all.len(), 1); // Only src/main.py (demo_files is in default ignore)

        // Collect with custom exclude
        let exclude = vec!["src".to_string()];
        let files_excluded = collect_files(base_path, &exclude).unwrap();
        assert_eq!(files_excluded.len(), 0); // Both excluded
    }
}
