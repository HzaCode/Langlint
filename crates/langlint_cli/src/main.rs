//! Langlint CLI - Command Line Interface for translation linting

use anyhow::Result;
use clap::{Parser, Subcommand};
use colored::Colorize;

mod commands;

use commands::{fix, scan, translate};

/// Langlint - Intelligent translation management for code and documentation
#[derive(Parser)]
#[command(name = "langlint")]
#[command(version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Enable verbose output
    #[arg(short, long, global = true)]
    verbose: bool,

    /// Output format (text, json, or pretty-json)
    #[arg(short, long, default_value = "text", global = true)]
    format: String,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan files and extract translatable units
    Scan {
        /// Input file or directory to scan
        #[arg(value_name = "PATH")]
        path: String,

        /// File patterns to include (glob)
        #[arg(short, long)]
        include: Option<Vec<String>>,

        /// File patterns to exclude (glob)
        #[arg(short, long)]
        exclude: Option<Vec<String>>,

        /// Only show units of specific types (comment, docstring, string, etc.)
        #[arg(short = 't', long)]
        unit_types: Option<Vec<String>>,

        /// Minimum priority level (high, medium, low)
        #[arg(short, long)]
        priority: Option<String>,

        /// Output file path (optional, defaults to stdout)
        #[arg(short, long)]
        output: Option<String>,
    },

    /// Translate text from one language to another
    Translate {
        /// Input file or directory to translate
        #[arg(value_name = "PATH")]
        path: String,

        /// Source language code (e.g., en, zh, ja)
        #[arg(short, long)]
        source: String,

        /// Target language code (e.g., en, zh, ja)
        #[arg(short, long)]
        target: String,

        /// Translator to use (mock, google, openai, deepl)
        #[arg(long, default_value = "google")]
        translator: String,

        /// Output file (default: overwrite input)
        #[arg(short, long)]
        output: Option<String>,

        /// Dry run (don't write changes)
        #[arg(long)]
        dry_run: bool,
    },

    /// Fix (in-place translate) files with automatic backup
    Fix {
        /// Input file or directory to fix
        #[arg(value_name = "PATH")]
        path: String,

        /// Source language code (e.g., en, zh, ja, auto)
        #[arg(short, long, default_value = "auto")]
        source: String,

        /// Target language code (e.g., en, zh, ja)
        #[arg(short = 't', long, default_value = "en")]
        target: String,

        /// Translator to use (mock, google, openai, deepl)
        #[arg(long, default_value = "google")]
        translator: String,

        /// Skip confirmation prompt
        #[arg(short, long)]
        yes: bool,

        /// Disable automatic backup creation
        #[arg(long)]
        no_backup: bool,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Setup logging/verbosity
    if cli.verbose {
        println!("{}", "Verbose mode enabled".dimmed());
    }

    match cli.command {
        Commands::Scan {
            path,
            include,
            exclude,
            unit_types,
            priority,
            output,
        } => {
            scan::execute(
                &path,
                include,
                exclude,
                unit_types,
                priority,
                output.as_deref(),
                &cli.format,
                cli.verbose,
            )
            .await
        }
        Commands::Translate {
            path,
            source,
            target,
            translator,
            output,
            dry_run,
        } => {
            translate::execute(
                &path,
                &source,
                &target,
                &translator,
                output.as_deref(),
                dry_run,
                &cli.format,
                cli.verbose,
            )
            .await
        }
        Commands::Fix {
            path,
            source,
            target,
            translator,
            yes,
            no_backup,
        } => {
            fix::execute(
                &path,
                &source,
                &target,
                &translator,
                yes,
                no_backup,
                &cli.format,
                cli.verbose,
            )
            .await
        }
    }
}
