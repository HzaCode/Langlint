//! Scan command implementation

use anyhow::{Context, Result};
use colored::Colorize;
use langlint_core::ParseResult;
use langlint_parsers::{GenericCodeParser, Parser, PythonParser};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

/// Execute the scan command
#[allow(clippy::too_many_arguments)]
pub async fn execute(
    path: &str,
    include: Option<Vec<String>>,
    exclude: Option<Vec<String>>,
    unit_types: Option<Vec<String>>,
    priority: Option<String>,
    output: Option<&str>,
    format: &str,
    verbose: bool,
) -> Result<()> {
    if verbose {
        println!("{} {}", "Scanning:".bold().cyan(), path);
    }

    let path_obj = Path::new(path);
    
    // Collect files to scan
    let files = collect_files(path_obj, include.as_ref(), exclude.as_ref())?;
    
    if verbose {
        println!("{} {} files found", "Total:".bold(), files.len());
    }

    // Scan all files
    let mut all_results = Vec::new();
    let mut total_units = 0;

    for file_path in &files {
        if verbose {
            println!("{} {}", "Processing:".dimmed(), file_path.display());
        }

        match scan_file(file_path).await {
            Ok(result) => {
                let units_count = result.units.len();
                total_units += units_count;
                
                if verbose && units_count > 0 {
                    println!(
                        "  {} {} translatable units",
                        "Found:".green(),
                        units_count
                    );
                }
                
                all_results.push((file_path.clone(), result));
            }
            Err(e) => {
                eprintln!(
                    "{} Failed to scan {}: {}",
                    "Warning:".yellow(),
                    file_path.display(),
                    e
                );
            }
        }
    }

    // Filter by unit types and priority if specified
    if let Some(ref types) = unit_types {
        all_results = filter_by_unit_types(all_results, types);
    }
    if let Some(ref prio) = priority {
        all_results = filter_by_priority(all_results, prio)?;
    }

    // Output results
    let output_content = format_results(&all_results, format, verbose)?;
    
    // Write to file or stdout
    if let Some(output_path) = output {
        fs::write(output_path, &output_content)
            .with_context(|| format!("Failed to write to: {}", output_path))?;
        if verbose {
            println!("{} Results written to: {}", "✓".green(), output_path);
        }
    } else {
        print!("{}", output_content);
    }

    // Summary
    if verbose || output.is_none() {
        println!("\n{}", "Summary:".bold().green());
        println!("  Files scanned: {}", files.len());
        println!("  Total translatable units: {}", total_units);
    }

    Ok(())
}

/// Collect files to scan based on include/exclude patterns
fn collect_files(
    path: &Path,
    include: Option<&Vec<String>>,
    exclude: Option<&Vec<String>>,
) -> Result<Vec<PathBuf>> {
    let mut files = Vec::new();

    if path.is_file() {
        files.push(path.to_path_buf());
        return Ok(files);
    }

    // Walk directory
    for entry in WalkDir::new(path)
        .follow_links(true)
        .into_iter()
        .filter_entry(|e| {
            // Skip hidden directories and common exclusions
            let name = e.file_name().to_string_lossy();
            !name.starts_with('.')
                && name != "node_modules"
                && name != "target"
                && name != "__pycache__"
                && name != "venv"
        })
    {
        let entry = entry?;
        if entry.file_type().is_file() {
            let file_path = entry.path();
            
            // Apply include/exclude patterns
            if should_include_file(file_path, include, exclude) {
                files.push(file_path.to_path_buf());
            }
        }
    }

    Ok(files)
}

/// Check if a file should be included based on patterns
fn should_include_file(
    path: &Path,
    include: Option<&Vec<String>>,
    exclude: Option<&Vec<String>>,
) -> bool {
    let path_str = path.to_string_lossy();

    // Check exclude patterns first
    if let Some(excludes) = exclude {
        for pattern in excludes {
            if path_str.contains(pattern) {
                return false;
            }
        }
    }

    // Check include patterns
    if let Some(includes) = include {
        for pattern in includes {
            if path_str.contains(pattern) {
                return true;
            }
        }
        return false; // If include patterns specified but none matched
    }

    true // Include by default
}

/// Scan a single file and extract translatable units
async fn scan_file(path: &Path) -> Result<ParseResult> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path.display()))?;

    let path_str = path.to_string_lossy();
    
    // Try Python parser first
    let python_parser = PythonParser::new();
    if python_parser.can_parse(&path_str, Some(&content)) {
        return python_parser
            .extract_units(&content, &path_str)
            .with_context(|| format!("Failed to parse Python file: {}", path.display()));
    }

    // Try generic code parser
    let generic_parser = GenericCodeParser::new();
    if generic_parser.can_parse(&path_str, Some(&content)) {
        return generic_parser
            .extract_units(&content, &path_str)
            .with_context(|| format!("Failed to parse file: {}", path.display()));
    }

    // No suitable parser found
    Ok(ParseResult {
        units: Vec::new(),
        file_type: "unknown".to_string(),
        encoding: "utf-8".to_string(),
        line_count: content.lines().count() as u32,
        metadata: None,
    })
}

/// Filter results by unit types
fn filter_by_unit_types(
    results: Vec<(PathBuf, ParseResult)>,
    types: &[String],
) -> Vec<(PathBuf, ParseResult)> {
    results
        .into_iter()
        .map(|(path, mut result)| {
            result.units.retain(|unit| {
                let unit_type_str = format!("{:?}", unit.unit_type).to_lowercase();
                types.iter().any(|t| unit_type_str.contains(&t.to_lowercase()))
            });
            (path, result)
        })
        .collect()
}

/// Filter results by priority
fn filter_by_priority(
    results: Vec<(PathBuf, ParseResult)>,
    priority: &str,
) -> Result<Vec<(PathBuf, ParseResult)>> {
    use langlint_core::Priority;

    let min_priority = match priority.to_lowercase().as_str() {
        "high" => Priority::High,
        "medium" => Priority::Medium,
        "low" => Priority::Low,
        _ => anyhow::bail!("Invalid priority: {}. Use high, medium, or low", priority),
    };

    Ok(results
        .into_iter()
        .map(|(path, mut result)| {
            result.units.retain(|unit| {
                matches!(
                    (min_priority, unit.priority),
                    (Priority::Low, _)
                        | (Priority::Medium, Priority::Medium | Priority::High)
                        | (Priority::High, Priority::High)
                )
            });
            (path, result)
        })
        .collect())
}

/// Format scan results in the specified format (returns string instead of printing)
fn format_results(
    results: &[(PathBuf, ParseResult)],
    format: &str,
    verbose: bool,
) -> Result<String> {
    match format {
        "json" => format_json(results, false),
        "pretty-json" => format_json(results, true),
        _ => format_text(results, verbose),
    }
}

/// Format results as JSON
fn format_json(results: &[(PathBuf, ParseResult)], pretty: bool) -> Result<String> {
    use serde::Serialize;

    #[derive(Serialize)]
    struct JsonOutput {
        files: Vec<FileOutput>,
    }

    #[derive(Serialize)]
    struct FileOutput {
        path: String,
        units: Vec<UnitOutput>,
    }

    #[derive(Serialize)]
    struct UnitOutput {
        content: String,
        unit_type: String,
        priority: String,
        line_start: usize,
        line_end: usize,
        #[serde(skip_serializing_if = "Option::is_none")]
        detected_language: Option<String>,
    }

    let output = JsonOutput {
        files: results
            .iter()
            .map(|(path, result)| FileOutput {
                path: path.display().to_string(),
                units: result
                    .units
                    .iter()
                    .map(|unit| UnitOutput {
                        content: unit.content.clone(),
                        unit_type: format!("{:?}", unit.unit_type),
                        priority: format!("{:?}", unit.priority),
                        line_start: unit.line_number as usize,
                        line_end: unit.line_number as usize,
                        detected_language: unit.detected_language.clone(),
                    })
                    .collect(),
            })
            .collect(),
    };

    if pretty {
        Ok(serde_json::to_string_pretty(&output)?)
    } else {
        Ok(serde_json::to_string(&output)?)
    }
}

/// Format results as human-readable text
fn format_text(results: &[(PathBuf, ParseResult)], verbose: bool) -> Result<String> {
    let mut output = String::new();
    output.push_str(&format!("\n{}\n", "=== Scan Results ==="));

    for (path, result) in results {
        if result.units.is_empty() {
            continue;
        }

        output.push_str(&format!("\n{} {}\n", "File:", path.display()));
        output.push_str(&format!("{} {} units\n", "Units:", result.units.len()));

        if verbose {
            for (i, unit) in result.units.iter().enumerate() {
                output.push_str(&format!("\n  {} {}:\n", "Unit", i + 1));
                output.push_str(&format!("    Type: {:?}\n", unit.unit_type));
                output.push_str(&format!("    Priority: {:?}\n", unit.priority));
                output.push_str(&format!(
                    "    Location: line {}, column {}\n",
                    unit.line_number, unit.column_number
                ));
                
                // Truncate long content
                let content = if unit.content.len() > 100 {
                    format!("{}...", &unit.content[..100])
                } else {
                    unit.content.clone()
                };
                output.push_str(&format!("    Content: {}\n", content));
            }
        }
    }

    Ok(output)
}

