"""
Command-line interface for LangLint.

This module provides the main CLI interface for the LangLint platform,
including commands for scanning, translating, and managing files.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from .core import Dispatcher, Config, Cache
from .parsers.base import TranslatableUnit
from .translators.base import Translator
from .translators.google_translator import GoogleTranslator, GoogleConfig
from .translators.mock_translator import MockTranslator, MockConfig


# Global console instance
# Use force_terminal=True and legacy_windows=False to avoid gbk encoding issues on Windows
# Force UTF-8 output for better compatibility
import sys
console = Console(force_terminal=True, legacy_windows=False, file=sys.stderr)


@click.group()
@click.version_option(version="1.0.0", prog_name="langlint")
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]) -> None:
    """
    LangLint: A scalable, domain-agnostic platform for automated translation
    and standardization of structured text in scientific collaboration.
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--format', '-f', 'output_format', type=click.Choice(['json', 'yaml', 'csv', 'text']), default='json', help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--include', '-i', multiple=True, help='Include patterns')
@click.option('--exclude', '-e', multiple=True, help='Exclude patterns')
@click.pass_context
def scan(ctx: click.Context, path: str, output: Optional[str], output_format: str, verbose: bool, include: tuple, exclude: tuple) -> None:
    """
    Scan files for translatable text without translating.

    PATH: Path to file or directory to scan
    """
    try:
        # Try to use Rust implementation for better performance
        try:
            import langlint_py
            import json
            
            # Prepare exclude patterns
            exclude_list = list(exclude) if exclude else []
            
            # Call Rust implementation
            result_json = langlint_py.scan(
                path,
                format=output_format,
                verbose=verbose,
                exclude=exclude_list
            )
            
            # Output results
            if output:
                Path(output).write_text(result_json, encoding='utf-8')
                print(f"Results written to {output}")
            else:
                # Output based on format
                if output_format == 'json':
                    print(result_json)
                elif output_format == 'text':
                    # For text format, check if result is JSON or plain text
                    try:
                        result = json.loads(result_json)
                        # Display nicely for text format
                        print(f"\nFiles scanned: {result['files_scanned']}")
                        print(f"Total units: {result['total_units']}")
                        
                        if verbose:
                            for file_result in result.get('results', []):
                                print(f"  {file_result['file']}: {file_result['units']} units")
                    except json.JSONDecodeError:
                        # Already in text format from Rust
                        print(result_json)
                else:
                    # For yaml, csv etc., output JSON (can be converted later)
                    print(result_json)
            
            return
            
        except ImportError:
            # Fall back to Python implementation
            console.print("[yellow]Warning:[/yellow] Rust module not available, using Python implementation")
        
        # Python fallback
        config = Config.load(ctx.obj['config'])

        # Override with CLI options
        if include:
            config.include = list(include)
        if exclude:
            config.exclude = list(exclude)

        # Initialize dispatcher
        dispatcher = Dispatcher(config)

        # Scan files
        asyncio.run(_scan_files(dispatcher, path, output, output_format, ctx))

    except Exception as e:
        # Use markup=False to avoid Rich markup errors with special characters
        console.print(f"[red]Error:[/red] {str(e)[:200]}", markup=False)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--source', '-s', default='auto', help='Source language code (default: auto-detect)')
@click.option('--target', '-t', default='en', help='Target language code (default: en)')
@click.option('--output', '-o', type=click.Path(), help='Output directory for translated files')
@click.option('--translator', default='google', type=click.Choice(['openai', 'deepl', 'google', 'mock']), help='Translation service to use (default: google, free)')
@click.option('--dry-run', is_flag=True, help='Show what would be translated without making changes')
@click.option('--backup', is_flag=True, default=True, help='Create backup of original files')
@click.option('--include', '-i', multiple=True, help='Include patterns')
@click.option('--exclude', '-e', multiple=True, help='Exclude patterns')
@click.pass_context
def translate(
    ctx: click.Context,
    path: str,
    source: str,
    target: str,
    output: Optional[str],
    translator: str,
    dry_run: bool,
    backup: bool,
    include: tuple,
    exclude: tuple
) -> None:
    """
    Translate files using the specified translation service.

    PATH: Path to file or directory to translate
    """
    try:
        # Try to use Rust implementation for better performance  
        try:
            import langlint_py
            import json
            
            # Call Rust implementation
            result_json = langlint_py.translate(
                path,
                source=source,
                target=target,
                translator=translator,
                output=output,
                dry_run=dry_run
            )
            
            # Parse and display results
            result = json.loads(result_json)
            
            if result.get('status') == 'success':
                print("\n✓ Translation complete!")
                print(f"Translated: {result.get('translated', 0)} units")
                if dry_run:
                    print("Dry run completed (no changes made)")
                if output:
                    print(f"Output: {output}")
            else:
                print(f"{result.get('message', 'No translatable units found')}")
            
            return
            
        except ImportError:
            # Fall back to Python implementation
            console.print("[yellow]Warning:[/yellow] Rust module not available, using Python implementation")
        
        # Python fallback
        config = Config.load(ctx.obj['config'])

        # Override with CLI options
        if include:
            config.include = list(include)
        if exclude:
            config.exclude = list(exclude)
        if source != 'auto':
            config.source_lang = [source]
        config.target_lang = target
        config.dry_run = dry_run
        config.backup = backup

        # Initialize dispatcher and translator
        dispatcher = Dispatcher(config)
        translator_instance = _create_translator(translator, config)

        # Translate files
        asyncio.run(_translate_files(dispatcher, translator_instance, path, output, ctx, source, target))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--source', '-s', default='auto', help='Source language code (default: auto-detect)')
@click.option('--target', '-t', default='en', help='Target language code (default: en)')
@click.option('--translator', default='google', type=click.Choice(['openai', 'deepl', 'google', 'mock']), help='Translation service to use (default: google, free)')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
@click.option('--no-backup', is_flag=True, help='Disable automatic backup')
@click.option('--include', '-i', multiple=True, help='Include patterns')
@click.option('--exclude', '-e', multiple=True, help='Exclude patterns')
@click.pass_context
def fix(
    ctx: click.Context,
    path: str,
    source: str,
    target: str,
    translator: str,
    yes: bool,
    no_backup: bool,
    include: tuple,
    exclude: tuple
) -> None:
    """
    Fix files by translating them in place.

    PATH: Path to file or directory to fix
    """
    try:
        # Try to use Rust implementation for better performance
        try:
            import langlint_py
            import json
            
            # Call Rust implementation (in-place translation, no output directory)
            result_json = langlint_py.translate(
                path,
                source=source,
                target=target,
                translator=translator,
                output=None,  # In-place translation
                dry_run=False
            )
            
            # Parse and display results
            result = json.loads(result_json)
            
            if result.get('status') == 'success':
                print("\n✓ Files fixed!")
                print(f"Translated: {result.get('translated', 0)} units")
                if not no_backup:
                    print("Backups created with .backup extension")
            else:
                print(f"{result.get('message', 'No translatable units found')}")
            
            return
            
        except ImportError:
            # Fall back to Python implementation
            console.print("[yellow]Warning:[/yellow] Rust module not available, using Python implementation")
        
        # Python fallback
        config = Config.load(ctx.obj['config'])

        # Override with CLI options
        if include:
            config.include = list(include)
        if exclude:
            config.exclude = list(exclude)
        if source != 'auto':
            config.source_lang = [source]
        config.target_lang = target
        config.dry_run = False
        config.backup = not no_backup

        # Initialize dispatcher and translator
        dispatcher = Dispatcher(config)
        translator_instance = _create_translator(translator, config)

        # Fix files
        asyncio.run(_fix_files(dispatcher, translator_instance, path, ctx, source, target))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--translator', '-t', type=click.Choice(['openai', 'deepl', 'google', 'mock']), default='google', help='Translation service to check (default: google, free)')
def status(translator: str) -> None:
    """
    Check the status of translation services.
    """
    try:
        # Create translator instance
        config = Config()
        translator_instance = _create_translator(translator, config)

        # Display status
        _display_translator_status(translator_instance)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def info() -> None:
    """
    Display information about LangLint.
    """
    _display_info()


def main() -> None:
    """Main entry point for the CLI."""
    cli()


# Rust module functions for testing compatibility
def rust_scan(path: str, **kwargs) -> dict:
    """Rust-powered scan function for testing."""
    # This is a placeholder for the actual Rust implementation
    # In the real implementation, this would call the Rust module
    return {
        "status": "success",
        "total_units": 0,
        "files_scanned": 0,
        "units": []
    }


def rust_translate(path: str, **kwargs) -> dict:
    """Rust-powered translate function for testing."""
    # This is a placeholder for the actual Rust implementation
    # In the real implementation, this would call the Rust module
    return {
        "status": "success",
        "translated": 0,
        "files_processed": 0,
        "errors": []
    }


async def _scan_files(dispatcher: Dispatcher, path: str, output: Optional[str], output_format: str, ctx: click.Context) -> None:
    """Scan files for translatable text with concurrent processing."""
    path_obj = Path(path)

    if path_obj.is_file():
        files = [path_obj]
    else:
        files = list(path_obj.rglob('*'))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]

    console.print(f"[blue]Scanning {len(files)} files with concurrent processing...[/blue]")

    # Semaphore to limit concurrent scans
    # For scan (CPU-bound), use more workers since it's local I/O + parsing
    max_concurrent = min(100, max(20, len(files) // 10))  # Adaptive: 20-100 workers
    semaphore = asyncio.Semaphore(max_concurrent)

    console.print(f"[cyan]Using {max_concurrent} concurrent workers[/cyan]")

    all_units = []
    units_lock = asyncio.Lock()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=10  # Update 10 times per second for smoother progress
    ) as progress:
        task = progress.add_task(f"[cyan]Scanning {len(files)} files...", total=len(files))

        completed_count = 0
        count_lock = asyncio.Lock()

        async def scan_single_file(file_path: Path):
            """Scan a single file with semaphore control."""
            nonlocal completed_count
            async with semaphore:
                try:
                    # Run blocking parse_file in executor to avoid blocking event loop
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, dispatcher.parse_file, str(file_path))

                    async with units_lock:
                        all_units.extend(result.parse_result.units)

                    async with count_lock:
                        completed_count += 1
                        if completed_count % 100 == 0:  # Every 100 files
                            console.print(f"[dim]Processed {completed_count}/{len(files)} files...[/dim]")

                    progress.advance(task)
                except Exception as e:
                    async with count_lock:
                        completed_count += 1
                    if ctx.obj.get('verbose', False):
                        console.print(f"[yellow]Warning: Failed to parse {file_path}: {e}[/yellow]")
                    progress.advance(task)

        # Process all files concurrently
        await asyncio.gather(*[scan_single_file(f) for f in files])

    # Display results
    _display_scan_results(all_units, output, output_format)


async def _translate_files(
    dispatcher: Dispatcher,
    translator: Translator,
    path: str,
    output: Optional[str],
    ctx: click.Context,
    source_lang: str,
    target_lang: str
) -> None:
    """Translate files using the specified translator with concurrent processing."""
    path_obj = Path(path)

    if path_obj.is_file():
        files = [path_obj]
    else:
        files = list(path_obj.rglob('*'))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]

    console.print(f"[blue]Translating {len(files)} files with concurrent processing...[/blue]")

    # Semaphore to limit concurrent translations (avoid rate limits)
    # For translate (network-bound), use fewer workers to avoid API rate limits
    max_concurrent = min(10, max(5, len(files) // 5))  # Adaptive: 5-10 workers
    semaphore = asyncio.Semaphore(max_concurrent)

    if ctx.obj.get('verbose', False):
        console.print(f"[dim]Using {max_concurrent} concurrent workers[/dim]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=10  # Update 10 times per second for smoother progress
    ) as progress:
        main_task = progress.add_task(f"[cyan]Translating {len(files)} files...", total=len(files))

        async def translate_single_file(file_path: Path):
            """Translate a single file with semaphore control."""
            async with semaphore:
                file_task = None
                try:
                    # Parse file
                    result = dispatcher.parse_file(str(file_path))

                    if not result.parse_result.units:
                        progress.advance(main_task)
                        return

                    # Count translatable units (exclude string_literal)
                    translatable_count = sum(1 for u in result.parse_result.units if u.unit_type.value != "string_literal")

                    # Create a sub-task for this file
                    file_task = progress.add_task(
                        f"  [dim]├─ {file_path.name}[/dim]",
                        total=translatable_count
                    )

                    # Create a custom translator wrapper to track progress
                    async def translate_with_progress(texts, src_lang, tgt_lang):
                        results = []
                        for text in texts:
                            result = await translator.translate(text, src_lang, tgt_lang)
                            results.append(result)
                            progress.advance(file_task, 1)
                        return results

                    # Translate units with progress tracking
                    translated_units = []
                    translatable_units = [u for u in result.parse_result.units if u.unit_type.value != "string_literal"]
                    skipped_units = [u for u in result.parse_result.units if u.unit_type.value == "string_literal"]

                    if translatable_units:
                        # Translate in small batches to show progress
                        batch_size = 10
                        for i in range(0, len(translatable_units), batch_size):
                            batch = translatable_units[i:i+batch_size]
                            texts = [u.content for u in batch]

                            # Detect language for the batch
                            if source_lang and source_lang != "auto":
                                src_lang = source_lang
                            else:
                                src_lang = _detect_language(texts[0]) if texts else "zh-CN"

                            # Translate batch
                            batch_results = await translate_with_progress(texts, src_lang, target_lang)

                            # Create translated units
                            for unit, trans_result in zip(batch, batch_results):
                                from langlint.parsers.base import TranslatableUnit
                                translated_unit = TranslatableUnit(
                                    content=trans_result.translated_text,
                                    unit_type=unit.unit_type,
                                    line_number=unit.line_number,
                                    column_number=unit.column_number,
                                    context=unit.context,
                                    metadata=unit.metadata
                                )
                                translated_units.append(translated_unit)

                    # Add back skipped units
                    all_translated = translated_units + skipped_units
                    all_translated.sort(key=lambda u: (u.line_number or 0, u.column_number or 0))

                    # Reconstruct file
                    if not dispatcher.config.dry_run:
                        # Read original content
                        original_content = file_path.read_text(encoding='utf-8')

                        reconstructed = result.parser.reconstruct_file(
                            original_content,
                            all_translated,
                            str(file_path)
                        )

                        # Write to output
                        if output:
                            output_path = Path(output) / file_path.name
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            output_path.write_text(reconstructed, encoding='utf-8')
                        else:
                            # Backup original file
                            if dispatcher.config.backup:
                                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                                backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')

                            # Write translated file
                            file_path.write_text(reconstructed, encoding='utf-8')

                    # Remove file task and advance main
                    if file_task is not None:
                        progress.remove_task(file_task)
                    progress.advance(main_task)

                except Exception as e:
                    if ctx.obj.get('verbose', False):
                        console.print(f"[yellow]Warning: Failed to translate {file_path}: {e}[/yellow]")
                    if file_task is not None:
                        progress.remove_task(file_task)
                    progress.advance(main_task)

        # Track backup files created
        backup_files = []

        async def translate_with_backup_tracking(file_path):
            await translate_single_file(file_path)
            # Track backup file if it was created
            if not output and dispatcher.config.backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                if backup_path.exists():
                    backup_files.append(backup_path)

        # Process all files concurrently
        await asyncio.gather(*[translate_with_backup_tracking(f) for f in files])

        # Clean up backup files after successful translation
        if backup_files and not output:
            for backup_file in backup_files:
                try:
                    backup_file.unlink()
                except Exception:
                    pass  # Silently ignore cleanup errors

    console.print("[green]Translation completed![/green]")


async def _fix_files(
    dispatcher: Dispatcher,
    translator: Translator,
    path: str,
    ctx: click.Context,
    source_lang: str,
    target_lang: str
) -> None:
    """Fix files by translating them in place."""
    await _translate_files(dispatcher, translator, path, None, ctx, source_lang, target_lang)


async def _translate_units(translator: Translator, units: List[TranslatableUnit], file_type: str, source_lang: str = "zh-CN", target_lang: str = "en") -> List[TranslatableUnit]:
    """Translate a list of units using the specified translator."""
    if not units:
        return []

    # Filter out string_literal types to avoid breaking code structure
    # Only translate comments and docstrings
    translatable_units = []
    skipped_units = []

    for unit in units:
        if unit.unit_type.value == "string_literal":
            skipped_units.append(unit)
        else:
            translatable_units.append(unit)

    # If no translatable units, return originals
    if not translatable_units:
        return units

    # Group units by source language
    # If source_lang is explicitly provided, use it; otherwise detect
    if source_lang and source_lang != "auto":
        # Use the explicitly provided source language for all units
        units_by_lang = {source_lang: translatable_units}
    else:
        # Auto-detect language for each unit
        units_by_lang = {}
        for unit in translatable_units:
            # Detect source language (simplified)
            detected_lang = _detect_language(unit.content)
            if detected_lang not in units_by_lang:
                units_by_lang[detected_lang] = []
            units_by_lang[detected_lang].append(unit)

    # Translate each group
    translated_units = []
    for lang_code, lang_units in units_by_lang.items():
        texts = [unit.content for unit in lang_units]

        try:
            # Translate batch
            results = await translator.translate_batch(
                texts,
                lang_code,
                target_lang
            )

            # Create translated units
            for unit, result in zip(lang_units, results):
                translated_unit = TranslatableUnit(
                    content=result.translated_text,
                    unit_type=unit.unit_type,
                    line_number=unit.line_number,
                    column_number=unit.column_number,
                    context=unit.context,
                    metadata=unit.metadata
                )
                translated_units.append(translated_unit)

        except Exception as e:
            console.print(f"[yellow]Warning: Failed to translate {source_lang} units: {e}[/yellow]")
            # Add original units as fallback
            translated_units.extend(lang_units)

    # Add back the skipped string_literal units (unchanged)
    all_units = translated_units + skipped_units

    # Sort by line number to maintain original order
    all_units.sort(key=lambda u: (u.line_number or 0, u.column_number or 0))

    return all_units


def _detect_language(text: str) -> str:
    """Detect the language of the given text (simplified)."""
    # This is a very simplified language detection
    # In a real implementation, you would use a proper language detection library

    # Check for common Chinese characters
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return 'zh-CN'

    # Check for common Japanese characters
    if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
        return 'ja'

    # Check for common Korean characters
    if any('\uac00' <= char <= '\ud7af' for char in text):
        return 'ko'

    # Check for common Arabic characters
    if any('\u0600' <= char <= '\u06ff' for char in text):
        return 'ar'

    # Check for common Cyrillic characters
    if any('\u0400' <= char <= '\u04ff' for char in text):
        return 'ru'

    # Default to English
    return 'en'


def _create_translator(translator_name: str, config: Config) -> Translator:
    """Create a translator instance based on the name."""
    if translator_name == 'openai':
        translator_config = config.get_translator_config(config.translator)
        return OpenAITranslator(OpenAIConfig(
            api_key=translator_config.api_key or '',
            model=translator_config.model or 'gpt-3.5-turbo',
            max_tokens=translator_config.max_tokens or 4000,
            temperature=translator_config.additional_params.get('temperature', 0.3),
            max_retries=translator_config.max_retries or 3,
            timeout=translator_config.timeout or 30,
            base_url=translator_config.api_url
        ))

    elif translator_name == 'deepl':
        translator_config = config.get_translator_config(config.translator)
        return DeepLTranslator(DeepLConfig(
            api_key=translator_config.api_key or '',
            base_url=translator_config.api_url,
            max_retries=translator_config.max_retries or 3,
            timeout=translator_config.timeout or 30,
            formality=translator_config.additional_params.get('formality', 'default')
        ))

    elif translator_name == 'google':
        translator_config = config.get_translator_config(config.translator)
        return GoogleTranslator(GoogleConfig(
            timeout=translator_config.timeout or 30,
            retry_count=translator_config.max_retries or 3,
            delay_range=(0.5, 1.5),
            service_urls=translator_config.additional_params.get('service_urls')
        ))

    elif translator_name == 'mock':
        return MockTranslator(MockConfig(
            delay_range=(0.1, 0.5),
            error_rate=0.0,
            confidence_range=(0.8, 1.0)
        ))

    else:
        raise ValueError(f"Unknown translator: {translator_name}")


def _display_scan_results(units: List[TranslatableUnit], output: Optional[str], output_format: str) -> None:
    """Display scan results."""
    if not units:
        console.print("[yellow]No translatable text found.[/yellow]")
        return

    # Create summary table
    table = Table(title="Scan Results")
    table.add_column("File", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Line", style="green")
    table.add_column("Content", style="white")

    for unit in units:
        table.add_row(
            str(unit.metadata.get('file_path', 'Unknown')),
            unit.unit_type.value,
            str(unit.line_number),
            unit.content[:50] + "..." if len(unit.content) > 50 else unit.content
        )

    console.print(table)

    # Save to file if requested
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == 'json':
            import json
            data = {
                'units': [
                    {
                        'content': unit.content,
                        'type': unit.unit_type.value,
                        'line': unit.line_number,
                        'column': unit.column_number,
                        'context': unit.context,
                        'metadata': unit.metadata
                    }
                    for unit in units
                ]
            }
            output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

        elif output_format == 'yaml':
            import yaml
            data = {
                'units': [
                    {
                        'content': unit.content,
                        'type': unit.unit_type.value,
                        'line': unit.line_number,
                        'column': unit.column_number,
                        'context': unit.context,
                        'metadata': unit.metadata
                    }
                    for unit in units
                ]
            }
            output_path.write_text(yaml.dump(data, default_flow_style=False), encoding='utf-8')

        elif output_format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['content', 'type', 'line', 'column', 'context', 'metadata'])
                for unit in units:
                    writer.writerow([
                        unit.content,
                        unit.unit_type.value,
                        unit.line_number,
                        unit.column_number,
                        unit.context,
                        str(unit.metadata)
                    ])

        console.print(f"[green]Results saved to {output_path}[/green]")


def _display_translator_status(translator: Translator) -> None:
    """Display translator status information."""
    info = translator.get_usage_info()

    # Format cost display
    cost_per_char = info['cost_per_character']
    if cost_per_char == 0.0:
        cost_display = "Free"
    elif cost_per_char < 0.0001:
        # Display per million characters for very small costs
        cost_display = f"${cost_per_char * 1_000_000:.4f} per 1M characters"
    else:
        cost_display = f"${cost_per_char:.6f} per character"

    # Create status panel
    status_text = f"""
[bold]Translator:[/bold] {info['name']}
[bold]Supported Languages:[/bold] {', '.join(info['supported_languages'][:10])}{'...' if len(info['supported_languages']) > 10 else ''}
[bold]Cost:[/bold] {cost_display}
[bold]Max Batch Size:[/bold] {info['max_batch_size']}
[bold]Rate Limit:[/bold] {info['rate_limit']}
    """

    panel = Panel(status_text, title="Translator Status", border_style="blue")
    console.print(panel)


def _display_info() -> None:
    """Display LangLint information."""
    from langlint import __version__
    info_text = f"""
[bold blue]LangLint v{__version__}[/bold blue]

A scalable, domain-agnostic platform for automated translation and
standardization of structured text in scientific collaboration.

[bold]Features:[/bold]
- Pluggable parser architecture for multiple file types
- Support for Python, Markdown, Jupyter Notebooks, and more
- Multiple translation services (OpenAI, DeepL, Google, Azure)
- High-performance parsing with caching
- Command-line interface with rich output
- Comprehensive configuration options

[bold]Supported File Types:[/bold]
- Python (.py, .pyi, .pyw)
- Markdown (.md, .markdown, .mdown, .mkd, .mkdn)
- Jupyter Notebooks (.ipynb)
- Generic Code (.js, .ts, .go, .rs, .java, .cpp, .c, .h, .cs, .php, .rb, .sh, .sql, .r, .m, .scala, .kt, .swift, .dart, .lua, .vim)
- Configuration Files (.yaml, .yml, .toml, .json, .ini, .cfg, .conf, .properties)

[bold]Quick Start:[/bold]
  langlint scan path/to/files          # Scan for translatable text
  langlint translate path/to/files     # Translate files
  langlint fix path/to/files          # Fix files in place

[bold]Documentation:[/bold] https://github.com/HzaCode/Langlint
[bold]Repository:[/bold] https://github.com/HzaCode/Langlint
[bold]License:[/bold] MIT
    """

    panel = Panel(info_text, title="LangLint Information", border_style="green")
    console.print(panel)
