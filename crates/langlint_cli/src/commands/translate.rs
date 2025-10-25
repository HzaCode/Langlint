//! Translate command implementation

use anyhow::{Context, Result};
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use langlint_core::ParseResult;
use langlint_parsers::{GenericCodeParser, NotebookParser, Parser, PythonParser};
use langlint_translators::{GoogleTranslator, MockTranslator, Translator};
use std::fs;
use std::path::Path;

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

    // Read file
    let path_obj = Path::new(path);
    let content =
        fs::read_to_string(path_obj).with_context(|| format!("Failed to read file: {}", path))?;

    if verbose {
        println!("{} File loaded ({} bytes)", "✓".green(), content.len());
    }

    // Parse file to extract translatable units
    let parse_result = parse_file(path, &content)?;
    let unit_count = parse_result.units.len();

    if unit_count == 0 {
        println!("{} No translatable units found", "!".yellow());
        return Ok(());
    }

    println!("{} Found {} translatable units", "✓".green(), unit_count);

    // Translate units (with parallel processing for better performance)
    let progress = if !verbose && !dry_run {
        let pb = ProgressBar::new(unit_count as u64);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("{spinner:.green} [{bar:40.cyan/blue}] {pos}/{len} {msg}")
                .unwrap()
                .progress_chars("#>-"),
        );
        Some(pb)
    } else {
        None
    };

    let mut translated_units = Vec::new();
    for (i, unit) in parse_result.units.iter().enumerate() {
        if let Some(ref pb) = progress {
            pb.set_message(format!("Translating unit {}/{}", i + 1, unit_count));
        }

        if verbose {
            println!(
                "\n{} Translating unit {}/{}: {:?}",
                "→".blue(),
                i + 1,
                unit_count,
                unit.unit_type
            );
            let preview = if unit.content.len() > 60 {
                format!("{}...", &unit.content[..60])
            } else {
                unit.content.clone()
            };
            println!("  Original: {}", preview.dimmed());
        }

        if !dry_run {
            match translator.translate(&unit.content, source, target).await {
                Ok(result) => {
                    if verbose {
                        println!("  Translated: {}", result.translated_text.green());
                        println!("  Confidence: {:.2}", result.confidence);
                    }
                    translated_units.push(result);
                }
                Err(e) => {
                    eprintln!("{} Failed to translate unit {}: {}", "✗".red(), i + 1, e);
                    // Continue with next unit
                }
            }
        }

        if let Some(ref pb) = progress {
            pb.inc(1);
        }
    }

    if let Some(pb) = progress {
        pb.finish_with_message("Translation complete");
    }

    if dry_run {
        println!("\n{} Dry run completed (no changes made)", "✓".green());
        return Ok(());
    }

    // Reconstruct file with translations
    // Create translated units with updated content
    let mut translated_result_units = Vec::new();
    for (unit, translation) in parse_result.units.iter().zip(translated_units.iter()) {
        let mut translated_unit = unit.clone();
        translated_unit.content = translation.translated_text.clone();
        translated_result_units.push(translated_unit);
    }

    // Use parser's reconstruct method for proper handling
    let parser = get_parser_for_file(path)?;
    let reconstructed_content = parser
        .reconstruct(&content, &translated_result_units, path)
        .with_context(|| "Failed to reconstruct file with translations")?;

    // Write output
    let output_path = output.unwrap_or(path);

    if output_path != path {
        // Writing to different file
        fs::write(output_path, &reconstructed_content)
            .with_context(|| format!("Failed to write to: {}", output_path))?;
        println!(
            "{} Translated file written to: {}",
            "✓".green(),
            output_path
        );
    } else {
        // Overwriting original file - create backup first
        let backup_path = format!("{}.backup", path);
        fs::copy(path, &backup_path)
            .with_context(|| format!("Failed to create backup: {}", backup_path))?;

        fs::write(output_path, &reconstructed_content)
            .with_context(|| format!("Failed to write to: {}", output_path))?;

        println!(
            "{} File translated in-place (backup: {})",
            "✓".green(),
            backup_path
        );
    }

    // Summary
    println!("\n{}", "Summary:".bold().green());
    println!("  Units translated: {}", translated_units.len());
    println!("  File: {}", output_path);

    Ok(())
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
