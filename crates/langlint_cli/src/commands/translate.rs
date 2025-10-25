//! Translate command implementation

use anyhow::{Context, Result};
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use langlint_core::ParseResult;
use langlint_parsers::{GenericCodeParser, NotebookParser, Parser, PythonParser};
use langlint_translators::{GoogleTranslator, MockTranslator, Translator};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

/// Execute the translate command
#[allow(clippy::too_many_arguments)]
pub async fn execute(
    path: &str,
    source: &str,
    target: &str,
    translator_name: &str,
    output: Option<&str>,
    dry_run: bool,
    _format: &str,
    verbose: bool,
) -> Result<()> {
    if verbose {
        println!("{} {}", "Translating:".bold().cyan(), path);
        println!("  Source language: {}", source);
        println!("  Target language: {}", target);
        println!("  Translator: {}", translator_name);
        if dry_run {
            println!("  {}", "DRY RUN MODE".yellow().bold());
        }
    }

    // Create translator
    let translator: Box<dyn Translator> = match translator_name {
        "mock" => Box::new(MockTranslator::new()),
        "google" => Box::new(GoogleTranslator::new()?),
        _ => anyhow::bail!("Unknown translator: {}", translator_name),
    };

    if verbose {
        println!("{} Translator created", "✓".green());
    }

    let path_obj = Path::new(path);

    // Collect files to translate
    let files = collect_files(path_obj)?;

    if files.is_empty() {
        println!("{} No translatable files found", "!".yellow());
        return Ok(());
    }

    if verbose {
        println!("{} {} files found", "Total:".bold(), files.len());
    }

    // Setup progress bar
    let pb = ProgressBar::new(files.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("{spinner:.green} [{bar:40.cyan/blue}] {pos}/{len} {msg}")
            .unwrap()
            .progress_chars("=>-"),
    );

    let mut translated_count = 0;
    let mut error_count = 0;
    let mut total_units = 0;

    for file_path in &files {
        let filename = file_path.file_name().unwrap().to_string_lossy();
        pb.set_message(format!("Translating {}", filename));

        // Determine output path for this file
        let output_file_path = if let Some(output_dir) = output {
            // Calculate relative path from input to maintain directory structure
            let relative_path = if path_obj.is_dir() {
                file_path.strip_prefix(path_obj).unwrap_or(file_path)
            } else {
                file_path.file_name().map(Path::new).unwrap_or(file_path)
            };
            PathBuf::from(output_dir).join(relative_path)
        } else {
            file_path.clone()
        };

        match translate_single_file(
            file_path,
            &output_file_path,
            source,
            target,
            translator.as_ref(),
            dry_run,
            verbose,
        )
        .await
        {
            Ok(units) => {
                if units > 0 {
                    translated_count += 1;
                    total_units += units;
                    if verbose {
                        pb.println(format!(
                            "{} {} → {} ({} units)",
                            "✓".green(),
                            file_path.display(),
                            output_file_path.display(),
                            units
                        ));
                    }
                }
            }
            Err(e) => {
                error_count += 1;
                pb.println(format!(
                    "{} Failed to translate {}: {}",
                    "✗".red(),
                    file_path.display(),
                    e
                ));
            }
        }

        pb.inc(1);
    }

    pb.finish_with_message("Translation complete");

    // Summary
    println!("\n{}", "Summary:".bold().green());
    println!("  Files processed: {}", files.len());
    println!("  Files translated: {}", translated_count);
    println!("  Total units translated: {}", total_units);
    if error_count > 0 {
        println!("  {} Errors: {}", "⚠".yellow(), error_count);
    }

    if dry_run {
        println!("\n{} Dry run completed (no changes made)", "✓".green());
    } else if let Some(output_dir) = output {
        println!(
            "\n{} Translation complete! Files written to: {}",
            "✓".green().bold(),
            output_dir
        );
    } else {
        println!(
            "\n{} Translation complete! Files overwritten (backups created with .backup extension)",
            "✓".green().bold()
        );
    }

    Ok(())
}

/// Translate a single file
async fn translate_single_file(
    input_path: &Path,
    output_path: &Path,
    source: &str,
    target: &str,
    translator: &dyn Translator,
    dry_run: bool,
    verbose: bool,
) -> Result<usize> {
    // Read file
    let content = fs::read_to_string(input_path)
        .with_context(|| format!("Failed to read file: {}", input_path.display()))?;

    let path_str = input_path.to_string_lossy();

    // Parse file to extract translatable units
    let parse_result = parse_file(&path_str, &content)?;
    let unit_count = parse_result.units.len();

    if unit_count == 0 {
        if verbose {
            println!("  {} No translatable units", "→".dimmed());
        }
        return Ok(0);
    }

    if verbose {
        println!("  Found {} translatable units", unit_count);
    }

    if dry_run {
        return Ok(unit_count);
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

    // Reconstruct file with translations
    let parser = get_parser_for_file(&path_str)?;
    let reconstructed = parser.reconstruct(&content, &translated_units, &path_str)?;

    // Create output directory if needed
    if let Some(parent) = output_path.parent() {
        fs::create_dir_all(parent)
            .with_context(|| format!("Failed to create directory: {}", parent.display()))?;
    }

    // If output path is the same as input path, create backup
    if output_path == input_path {
        let backup_path = format!("{}.backup", input_path.display());
        fs::copy(input_path, &backup_path)
            .with_context(|| format!("Failed to create backup: {}", backup_path))?;

        if verbose {
            println!("  {} Backup created: {}", "✓".green(), backup_path);
        }
    }

    // Write output
    fs::write(output_path, reconstructed)
        .with_context(|| format!("Failed to write to: {}", output_path.display()))?;

    Ok(unit_count)
}

/// Collect files to translate
fn collect_files(path: &Path) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();

    if path.is_file() {
        if should_translate(path) {
            files.push(path.to_path_buf());
        }
        return Ok(files);
    }

    let root_path = path.to_path_buf();

    // Walk directory
    for entry in WalkDir::new(path)
        .follow_links(true)
        .into_iter()
        .filter_entry(|e| {
            // Don't filter the root directory itself
            if e.path() == root_path {
                return true;
            }
            
            let name = e.file_name().to_string_lossy();
            !name.starts_with('.')
                && name != "node_modules"
                && name != "target"
                && name != "__pycache__"
                && name != "venv"
                && name != ".venv"
                && name != "build"
                && name != "dist"
        })
    {
        let entry = entry?;
        if entry.file_type().is_file() && should_translate(entry.path()) {
            files.push(entry.path().to_path_buf());
        }
    }

    Ok(files)
}

/// Check if a file should be translated
fn should_translate(path: &Path) -> bool {
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

/// Parse a file and extract translatable units
fn parse_file(path: &str, content: &str) -> Result<ParseResult> {
    let parser = get_parser_for_file(path)?;
    parser
        .extract_units(content, path)
        .with_context(|| format!("Failed to parse file: {}", path))
}

/// Get appropriate parser for a file
fn get_parser_for_file(path: &str) -> Result<Box<dyn Parser>> {
    // Try Python parser first
    let python_parser = PythonParser::new();
    if python_parser.can_parse(path, None) {
        return Ok(Box::new(python_parser));
    }

    // Try Notebook parser
    let notebook_parser = NotebookParser::new();
    if notebook_parser.can_parse(path, None) {
        return Ok(Box::new(notebook_parser));
    }

    // Try generic code parser
    let generic_parser = GenericCodeParser::new();
    if generic_parser.can_parse(path, None) {
        return Ok(Box::new(generic_parser));
    }

    anyhow::bail!("No suitable parser found for file: {}", path)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_should_translate() {
        assert!(should_translate(Path::new("test.py")));
        assert!(should_translate(Path::new("test.js")));
        assert!(should_translate(Path::new("test.rs")));
        assert!(should_translate(Path::new("test.ipynb")));
        assert!(!should_translate(Path::new("test.txt")));
        assert!(!should_translate(Path::new("README.md")));
    }

    #[test]
    fn test_get_parser_for_file() {
        assert!(get_parser_for_file("test.py").is_ok());
        assert!(get_parser_for_file("test.js").is_ok());
        assert!(get_parser_for_file("test.ipynb").is_ok());
        assert!(get_parser_for_file("test.txt").is_err());
    }

    #[test]
    fn test_collect_files_single_file() {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test.py");
        fs::write(&file_path, "# test").unwrap();

        let files = collect_files(&file_path).unwrap();
        assert_eq!(files.len(), 1);
        assert_eq!(files[0], file_path);
    }

    #[test]
    fn test_collect_files_directory() {
        let temp_dir = TempDir::new().unwrap();
        
        // Create test files
        fs::write(temp_dir.path().join("test1.py"), "# test1").unwrap();
        fs::write(temp_dir.path().join("test2.js"), "// test2").unwrap();
        fs::write(temp_dir.path().join("readme.txt"), "readme").unwrap(); // Should be ignored

        let files = collect_files(temp_dir.path()).unwrap();
        assert_eq!(files.len(), 2); // Only .py and .js files
    }

    #[test]
    fn test_collect_files_ignores_hidden_directories() {
        let temp_dir = TempDir::new().unwrap();
        
        // Create a hidden directory
        let hidden_dir = temp_dir.path().join(".hidden");
        fs::create_dir(&hidden_dir).unwrap();
        fs::write(hidden_dir.join("test.py"), "# hidden").unwrap();
        
        // Create a normal file
        fs::write(temp_dir.path().join("test.py"), "# visible").unwrap();

        let files = collect_files(temp_dir.path()).unwrap();
        assert_eq!(files.len(), 1); // Only visible file
    }

    #[test]
    fn test_collect_files_ignores_common_directories() {
        let temp_dir = TempDir::new().unwrap();
        
        // Create ignored directories
        for dir_name in &["node_modules", "__pycache__", "target", "venv"] {
            let ignored_dir = temp_dir.path().join(dir_name);
            fs::create_dir(&ignored_dir).unwrap();
            fs::write(ignored_dir.join("test.py"), "# ignored").unwrap();
        }
        
        // Create a normal file
        fs::write(temp_dir.path().join("test.py"), "# visible").unwrap();

        let files = collect_files(temp_dir.path()).unwrap();
        assert_eq!(files.len(), 1); // Only visible file
    }

    #[test]
    fn test_collect_files_nested_directories() {
        let temp_dir = TempDir::new().unwrap();
        
        // Create nested structure
        let src_dir = temp_dir.path().join("src");
        let utils_dir = src_dir.join("utils");
        fs::create_dir_all(&utils_dir).unwrap();
        
        fs::write(temp_dir.path().join("main.py"), "# main").unwrap();
        fs::write(src_dir.join("lib.py"), "# lib").unwrap();
        fs::write(utils_dir.join("helper.py"), "# helper").unwrap();

        let files = collect_files(temp_dir.path()).unwrap();
        assert_eq!(files.len(), 3); // All .py files in all directories
    }
}
