//! Fix command implementation - In-place translation with automatic backup

use anyhow::{Context, Result};
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use langlint_core::Config;
use langlint_parsers::{GenericCodeParser, NotebookParser, Parser, PythonParser};
use langlint_translators::{GoogleTranslator, MockTranslator, Translator};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

/// Execute the fix command - translate files in-place with backup
#[allow(clippy::too_many_arguments)]
pub async fn execute(
    path: &str,
    source: &str,
    target: &str,
    translator_name: &str,
    yes: bool,
    no_backup: bool,
    _format: &str,
    verbose: bool,
) -> Result<()> {
    // Load config to get backup preference (if not overridden by CLI)
    let config = Config::find_and_load().unwrap_or_default();
    
    // Command line --no-backup flag overrides config file
    let should_backup = if no_backup {
        false  // Explicit --no-backup flag
    } else {
        config.backup  // Use config file setting (default: true)
    };
    
    if verbose {
        println!("{} {}", "Fixing (in-place translate):".bold().cyan(), path);
        println!("  Source language: {}", source);
        println!("  Target language: {}", target);
        println!("  Translator: {}", translator_name);
        println!("  Backup: {}", if should_backup { "enabled" } else { "disabled" });
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

    // Confirm before proceeding
    if !yes && !files.is_empty() {
        if should_backup {
            println!("\n{} About to translate {} files in-place (backups will be created)", 
                "⚠".yellow(), files.len());
        } else {
            println!("\n{} About to translate {} files in-place (⚠️  NO BACKUP will be created)", 
                "⚠".yellow(), files.len());
        }
        println!("  Press Enter to continue, Ctrl+C to cancel...");
        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
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

        match translate_file(file_path, source, target, translator.as_ref(), should_backup, verbose).await {
            Ok(units) => {
                if units > 0 {
                    translated_count += 1;
                    total_units += units;
                    if verbose {
                        pb.println(format!(
                            "{} {} ({} units)",
                            "✓".green(),
                            file_path.display(),
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

    pb.finish_with_message("Done!");

    // Summary
    println!("\n{}", "Summary:".bold().green());
    println!("  Files processed: {}", files.len());
    println!("  Files translated: {}", translated_count);
    println!("  Total units translated: {}", total_units);
    if error_count > 0 {
        println!("  {} Errors: {}", "⚠".yellow(), error_count);
    }

    if should_backup {
        println!("\n{} Translation complete! Backups created with .backup extension", 
            "✓".green().bold());
    } else {
        println!("\n{} Translation complete! (No backups created)", 
            "✓".green().bold());
    }

    Ok(())
}

/// Translate a single file in-place with backup
async fn translate_file(
    path: &Path,
    source: &str,
    target: &str,
    translator: &dyn Translator,
    should_backup: bool,
    verbose: bool,
) -> Result<usize> {
    // Read file
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))?;

    let path_str = path.to_string_lossy();

    // Parse file to extract translatable units
    let parse_result = match get_parser_for_file(&path_str) {
        Some(parser) => parser.extract_units(&content, &path_str)?,
        None => return Ok(0), // Skip files without parser
    };

    let unit_count = parse_result.units.len();

    if unit_count == 0 {
        if verbose {
            println!("  {} No translatable units", "→".dimmed());
        }
        return Ok(0);
    }

    // Translate all units
    let texts: Vec<String> = parse_result.units.iter()
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

    // Create backup (if enabled)
    if should_backup {
        let backup_path = format!("{}.backup", path.display());
        fs::copy(path, &backup_path)
            .with_context(|| format!("Failed to create backup: {}", backup_path))?;
        
        if verbose {
            println!("  {} Backup created: {}", "✓".green(), backup_path);
        }
    }

    // Reconstruct file with translations
    let parser = get_parser_for_file(&path_str)
        .ok_or_else(|| anyhow::anyhow!("No parser available"))?;
    let reconstructed = parser.reconstruct(&content, &translated_units, &path_str)?;

    // Write back to original file
    fs::write(path, reconstructed)
        .with_context(|| format!("Failed to write file: {}", path.display()))?;

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

    // Walk directory
    for entry in WalkDir::new(path)
        .follow_links(true)
        .into_iter()
        .filter_entry(|e| {
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
            "py" | "js" | "ts" | "jsx" | "tsx" | "rs" | "go" | "java" | 
            "c" | "cpp" | "h" | "hpp" | "cs" | "php" | "rb" | "sh" | "bash" |
            "sql" | "r" | "R" | "m" | "scala" | "kt" | "swift" | "dart" | 
            "lua" | "vim" | "ipynb"
        )
    } else {
        false
    }
}

/// Get appropriate parser for a file
fn get_parser_for_file(path: &str) -> Option<Box<dyn Parser>> {
    // Try Python parser
    let python_parser = PythonParser::new();
    if python_parser.can_parse(path, None) {
        return Some(Box::new(python_parser));
    }

    // Try Notebook parser
    let notebook_parser = NotebookParser::new();
    if notebook_parser.can_parse(path, None) {
        return Some(Box::new(notebook_parser));
    }

    // Try generic code parser
    let generic_parser = GenericCodeParser::new();
    if generic_parser.can_parse(path, None) {
        return Some(Box::new(generic_parser));
    }

    None
}

#[cfg(test)]
mod tests {
    use super::*;

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
        assert!(get_parser_for_file("test.py").is_some());
        assert!(get_parser_for_file("test.js").is_some());
        assert!(get_parser_for_file("test.ipynb").is_some());
        assert!(get_parser_for_file("test.txt").is_none());
    }
}
