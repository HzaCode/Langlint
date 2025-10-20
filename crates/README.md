# Langlint Rust Implementation

High-performance translation management system written in Rust.

## Architecture

```
langlint/
├── langlint_core/      # Core types and configuration
├── langlint_parsers/   # File parsers (Python, Generic, Notebook)
├── langlint_translators/  # Translation services (Mock, Google)
└── langlint_cli/       # Command-line interface
```

## Features

- **Multi-language parsing**: Python, JavaScript, TypeScript, Rust, Go, C/C++, Java, and 18+ more
- **Notebook support**: Jupyter Notebook (.ipynb) parsing
- **Multiple translators**: Mock (testing), Google Translate, extensible architecture
- **Async/concurrent**: Built on tokio for high performance
- **User-friendly CLI**: Progress bars, colored output, verbose logging
- **Safe operations**: Automatic backups, dry-run mode

## Usage

### Scan files for translatable content
```bash
cargo run -p langlint_cli -- scan path/to/file.py --verbose
cargo run -p langlint_cli -- scan . --format json
```

### Translate files
```bash
cargo run -p langlint_cli -- translate file.py --source en --target zh --translator mock
cargo run -p langlint_cli -- translate file.py -s en -t zh --translator google --dry-run
```

### Build release binary
```bash
cargo build --release
./target/release/langlint --help
```

## Testing

```bash
# Run all tests
cargo test --workspace

# Run specific module tests
cargo test -p langlint_core
cargo test -p langlint_parsers
cargo test -p langlint_translators

# With output
cargo test -- --nocapture
```

## Performance

- **2,600+ lines** of Rust code
- **16 modules** across 4 crates
- **Zero unsafe** code
- **31 tests** (28 passing, 2 network tests ignored, 1 doc test)
- **Release build**: Optimized binary ready for production

## Development Status

- ✅ Core types and configuration
- ✅ Python parser
- ✅ Generic code parser (18+ languages)
- ✅ Notebook parser
- ✅ Mock translator
- ✅ Google translator
- ✅ CLI (scan, translate commands)
- ✅ Progress bars and colored output
- ⏳ Fix command (coming soon)
- ⏳ OpenAI/DeepL translators (coming soon)

## Contributing

Built with:
- Rust 1.90+
- tokio (async runtime)
- clap (CLI framework)
- serde/serde_json (serialization)
- regex (parsing)
- reqwest (HTTP client)

## License

See LICENSE file in project root.

