<div align="center">

<img src="langlint_lightning_logo.png" alt="LangLint Logo" width="200"/>


# LangLint

**Breaking Language Barriers in Global Collaboration** 🚀 · **Now 10–50× Faster with Rust**

[![PyPI](https://img.shields.io/pypi/v/langlint.svg)](https://pypi.org/project/langlint/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rust](https://img.shields.io/badge/rust-1.90%2B-orange.svg)](https://www.rust-lang.org/)
[![CI](https://github.com/HzaCode/Langlint/workflows/CI/badge.svg)](https://github.com/HzaCode/Langlint/actions)
[![codecov](https://codecov.io/gh/HzaCode/Langlint/branch/main/graph/badge.svg)](https://codecov.io/gh/HzaCode/Langlint)
[![Documentation](https://img.shields.io/badge/docs-passing-brightgreen.svg)](https://github.com/HzaCode/Langlint)
[![Downloads](https://static.pepy.tech/badge/langlint?style=flat-square)](https://pepy.tech/project/langlint)

</div>

 **LangLint** is a high-performance, extensible, **Rust-powered, code-aware translation and linting toolkit** for code comments and documentation. It keeps multilingual scientific software docs consistent and reproducible, supporting **FAIR** and open-science practices.



## 🚀 Quick Start

### Installation (Same as Before!)

```bash
# Install via pip (now installs Rust-powered version)
pip install langlint

# Or use pipx for isolated environment
pipx install langlint

# Or use uv for fastest installation
uv tool install langlint
```

> 💡 **Zero Breaking Changes**: Your existing scripts work immediately. Just upgrade and enjoy 10-50x speedup!

### Basic Usage

```bash
# Scan translatable content (now 10x faster!)
langlint scan src/

# Translate (preserve original files)
langlint translate src/ -s zh-CN -t en -o output/

# In-place translation (auto backup)
langlint fix src/ -s zh-CN -t en
```

## 📸 Translation Demo

**Before** (Japanese code with comments):
```python
def calculate_total(items):
    """商品の合計金額を計算する"""
    total = 0
    for item in items:
        # 価格を累積
        total += item.price
    return total

def apply_discount(price, rate):
    """割引を適用する関数"""
    if rate < 0 or rate > 1:
        # 無効な割引率
        raise ValueError("割引率は0から1の間である必要があります")

    # 割引後の価格を計算
    discounted = price * (1 - rate)
    return round(discounted, 2)
```

**After** (One command: `langlint fix example.py -s ja -t en`):
```python
def calculate_total(items):
    """Calculate the total price of the product"""
    total = 0
    for item in items:
        # Accumulate prices
        total += item.price
    return total

def apply_discount(price, rate):
    """Function to apply discount"""
    if rate < 0 or rate > 1:
        # Invalid discount rate
        raise ValueError("Discount rate must be between 0 and 1")

    # Calculate discounted price
    discounted = price * (1 - rate)
    return round(discounted, 2)
```



✨ **Code still works perfectly!** Only comments and docstrings are translated.

### Core Commands

| Command | Function | Example |
|---------|----------|---------|
| `scan` | Scan translatable content | `langlint scan .` |
| `translate` | Translate to new directory | `langlint translate . -s auto -t en -o output/` |
| `fix` | In-place translate + backup | `langlint fix . -s auto -t en` |

**Default: Google Translate, Auto-detect → English** (Free, no API Key required)

**Available Translators:**

- `google` - Google Translate (Free, no API key needed) ✅
- `mock` - Mock translator for testing ✅

## ✨ Key Features

### 🌍 Multilingual Translation Support

- ✅ **100+ Language Pairs**: French↔English, German↔Chinese, Spanish↔Japanese, etc.
- ✅ **Smart Language Detection**: Auto-detect source language or specify manually
- ✅ **Syntax Protection**: Automatically excludes string literals and f-strings
- ✅ **High-Performance Concurrency**: Batch translation for multiple files (true parallelism in Rust!)

```bash
# Basic usage (auto-detect → English)
langlint fix src/

# European languages (French → English, specify source to avoid misdetection)
langlint fix french_code.py -s fr

# Translate to other languages (German → Chinese)
langlint fix german_code.py -s de -t zh-CN
```

<details>
<summary>📋 Supported Languages List</summary>

**European Languages**: English (en), French (fr), German (de), Spanish (es), Italian (it), Portuguese (pt), Russian (ru), Dutch (nl), Polish (pl), Swedish (sv)

**Asian Languages**: Simplified Chinese (zh-CN), Traditional Chinese (zh-TW), Japanese (ja), Korean (ko), Thai (th), Vietnamese (vi), Hindi (hi), Indonesian (id)

**Other Languages**: Arabic (ar), Hebrew (he), Turkish (tr), Greek (el), Persian (fa)

**Note**: European languages (French, German, Spanish, Italian, etc.) **must** use the `-s` parameter to specify source language, otherwise they will be misidentified as English!

</details>

### 🔌 Supported File Types (28+)

- **Python**: `.py`
- **JavaScript/TypeScript**: `.js`, `.ts`, `.jsx`, `.tsx`
- **Systems**: `.rs` (Rust), `.go`, `.c`, `.cpp`, `.h`, `.hpp`
- **JVM**: `.java`, `.scala`, `.kt` (Kotlin)
- **Others**: `.cs`, `.php`, `.rb`, `.swift`, `.dart`, `.lua`, `.sh`, `.bash`, `.sql`, `.r`, `.R`, `.m`, `.vim`

**What gets translated**: Comments and docstrings in code files. String literals and configuration values are preserved.

### ⚡ High Performance

**Rust-powered performance** is **10-50x faster** than the previous Python implementation! 🚀

True multi-threading (no GIL), zero-cost abstractions, and efficient memory management make LangLint blazing fast.

<details>
<summary>📖 Detailed Usage Guide (Click to expand)</summary>

### Basic Commands

```bash
# Scan translatable content
langlint scan path/to/files

# Translate to new directory
langlint translate path/to/files -o output/

# In-place translation (auto backup)
langlint fix path/to/files
```

### Multilingual Translation Scenarios

```bash
# Scenario 1: Translate French code comments to English
langlint scan french_project/ -o report.json --format json
langlint translate french_project/ -s fr -o english_project/

# Scenario 2: Internationalize codebase
langlint fix src/
pytest tests/  # Verify code still works

# Scenario 3: Translate JavaScript project
langlint fix frontend/ -s zh-CN -t en
```

### Advanced Parameters

```bash
# Exclude specific files
langlint translate src/ -o output/ -e "**/test_*" -e "**/__pycache__/"

# Dry-run preview
langlint translate src/ -s fr -t en --dry-run

# Use different translators
langlint translate src/ -s zh-CN -t en --translator google  # Google Translate (available now)
langlint translate src/ -s zh-CN -t en --translator mock    # Mock translator for testing
```

</details>

<details>
<summary>🔧 Python API Usage (Click to expand)</summary>

LangLint can be used as a library in your Python projects. The API is **100% compatible** with v0.0.6, but now runs on Rust!

#### Basic API Usage (Rust-Powered)

```python
# Import the Rust-powered module
import langlint_py

# Scan files (now 10x faster!)
result = langlint_py.scan(
    "src/",
    format="json",
    verbose=True
)
print(result)  # JSON output

# Translate (now 10x faster!)
result = langlint_py.translate(
    "example.py",
    source="zh",
    target="en",
    translator="google",  # or "mock"
    output="example_en.py",
    dry_run=False
)
print(result)  # {"status": "success", "translated": 9, ...}
```

#### Batch Processing Example

```python
import langlint_py
import json
from pathlib import Path

# Scan entire project
result_json = langlint_py.scan("src/", format="json")
result = json.loads(result_json)

print(f"Found {result['total_units']} translatable units in {result['files_scanned']} files")

# Translate all Python files
for py_file in Path("src").rglob("*.py"):
    print(f"Translating {py_file}...")
    langlint_py.translate(
        str(py_file),
        source="zh",
        target="en",
        translator="mock",
        dry_run=False
    )
```

#### Performance Comparison

```python
import time
import langlint_py

# Benchmark
start = time.time()
result = langlint_py.scan("large_project/", format="json")
elapsed = time.time() - start

print(f"Scanned in {elapsed*1000:.2f}ms (Rust-powered!)")
# Typical: 3-5ms for 1000 lines
# Python v0.0.6 would take: 40-50ms for the same
```

</details>

<details>
<summary>⚙️ Configuration File (Click to expand)</summary>


Just put the **`.langlint.yml`** file in the root directory of your project.

```yaml
# Global settings
translator: "google"  # google or mock
target_lang: "en"
source_lang: ["zh-CN", "ja", "ko"]
backup: true  # Create backup files before in-place translation (default: true)

# File processing
include:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"

exclude:
  - "**/node_modules/**"
  - "**/test_*"
  - "**/data/**"

# Path-specific overrides
path_configs:
  "**/tests/**":
    translator: "mock"
    backup: false  # Don't backup test files

  "**/docs/**":
    translator: "google"
    target_lang: "en"
```



**Backup Control**

The `backup` option controls whether backup files (`.backup` extension) are created during in-place translation:

```bash
# Use config file setting
langlint fix src/

# Force disable backup (overrides config)
langlint fix src/ --no-backup
```

**Priority**: `--no-backup` flag > config file `backup` setting > default (true)

Configuration is loaded by the Rust core for maximum performance.

</details>

## 🤖 CI/CD Integration

**Integrate into Your Workflow Like Ruff** - Automate multilingual code checking and translation!

Supports: GitHub Actions ✅ | GitLab CI ✅ | Azure Pipelines ✅ | Pre-commit Hooks ✅ | Docker ✅

### 🎯 Best Practice: Use with Ruff

```bash
# First, check code quality with Ruff
ruff check . --fix

# Then, translate with LangLint (now 10x faster with Rust!)
langlint fix .

# Finally, run Ruff again to ensure translated code meets standards
ruff check .
```

<details>
<summary>📋 View Complete CI/CD Integration Configuration (Click to expand)</summary>

Integrate LangLint into your CI/CD pipeline to automate multilingual code checking and translation, just as simple as using Ruff for code quality checks!

### GitHub Actions Integration ⭐ Recommended

#### 1️⃣ Automatic Translation Coverage Check

Add to `.github/workflows/langlint-check.yml`:

```yaml
name: LangLint Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 8 * * *'  # Daily check to catch new untranslated content

jobs:
  langlint-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install LangLint (Rust-powered!)
        run: |
          pip install langlint

      - name: Scan for translatable content
        run: |
          langlint scan . -o report.json --format json

      - name: Check translation requirements
        run: |
          # Check for translatable content
          if [ -s report.json ]; then
            echo "⚠️ Found translatable content. Run 'langlint translate' locally."
            cat report.json
          else
            echo "✅ No translatable content found."
          fi
```

#### 2️⃣ Auto-Translate and Create PR

Automatically translate Chinese code to English and create a Pull Request:

```yaml
name: Auto Translate

on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 8 * * *'  # Run daily at 8 AM UTC to keep translations fresh

jobs:
  translate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install LangLint (Rust-powered!)
        run: pip install langlint

      - name: Translate code
        run: |
          langlint translate src/ -o src_en/

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: auto translate to English'
          title: '🌐 Auto-translated code to English'
          body: |
            This PR contains auto-translated code from Chinese to English.

            **Translation Details:**
            - Source Language: Chinese (zh-CN)
            - Target Language: English (en)
            - Translator: Google Translate

            Please review carefully before merging.
          branch: auto-translate/en
          delete-branch: true
```

#### 3️⃣ Pre-commit Integration Check

Block commits containing untranslated Chinese comments:

```yaml
name: Pre-commit Check

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-translation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install LangLint (Rust-powered!)
        run: pip install langlint

      - name: Check for non-English content
        run: |
          # Scan for translatable content
          langlint scan . -o report.json --format json

          # Check if any non-English content exists
          # This checks for common non-English language codes
          if grep -qE '"(zh-CN|zh-TW|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi)"' report.json; then
            echo "❌ Found non-English content. Please translate before committing."
            echo "Run: langlint fix ."
            echo ""
            echo "Detected languages:"
            grep -oE '"(zh-CN|zh-TW|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi)"' report.json | sort -u
            exit 1
          fi

          echo "✅ All content is in English."
```

#### 4️⃣ Batch Translate Project Code

Automatically translate all code comments in a project:

```yaml
name: Translate Project

on:
  workflow_dispatch:  # Manual trigger

jobs:
  translate-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install LangLint (Rust-powered!)
        run: pip install langlint

      - name: Translate all code comments
        run: |
          # Translate Python files
          langlint fix src/ -s zh-CN -t en

          # Translate JavaScript files
          langlint fix frontend/ -s zh-CN -t en

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'chore: translate code comments to English'
          title: '🌐 Translated code comments'
          branch: translate-comments
```

### Pre-commit Hooks Integration

Like Ruff, add LangLint to your pre-commit configuration.

#### Install pre-commit

```bash
pip install pre-commit
```

#### Configure `.pre-commit-config.yaml`

**Option 1: Remote Hook (Recommended)** - Automatically installs LangLint when needed:

```yaml
repos:
  # LangLint - Check translatable content (Rust-powered!)
  - repo: https://github.com/HzaCode/Langlint
    rev: main  # ✅ Use 'main' to always get the latest updates and language coverage
    hooks:
      - id: langlint-scan

      # Optional: Auto-translate (use with caution)
      - id: langlint-fix
        stages: [manual]  # Manual trigger only

  # Ruff - Code checking (for comparison)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

> 💡 **Why use `rev: main`?** Keeping `rev: main` ensures you automatically benefit from the latest Langlint improvements, new language support, and bug fixes without manual updates. Perfect for rapidly evolving projects!

**Option 2: Local Hook** - Uses your locally installed LangLint:

```yaml
repos:
  # LangLint - Check translatable content (Rust-powered!)
  - repo: local
    hooks:
      - id: langlint-scan
        name: LangLint Scan
        entry: langlint scan
        language: system
        types: [python]
        pass_filenames: true
        verbose: true

      # Optional: Auto-translate (use with caution)
      - id: langlint-fix
        name: LangLint Auto-fix
        entry: langlint fix
        language: system
        types: [python]
        pass_filenames: true
        stages: [manual]  # Manual trigger only

  # Ruff - Code checking (for comparison)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

**Note**:
- **Remote hook**: pre-commit will automatically install LangLint in an isolated environment. No manual installation needed!
- **Local hook**: Requires `pip install langlint` first, but gives you control over the version.

#### Use pre-commit

```bash
# Install hooks
pre-commit install

# Auto-run on each commit
git commit -m "feat: add new feature"

# Manually run all hooks
pre-commit run --all-files

# Manually trigger translation
pre-commit run langlint-fix --all-files
```

### GitLab CI Integration

Add to `.gitlab-ci.yml`:

```yaml
stages:
  - lint
  - translate

langlint-check:
  stage: lint
  image: python:3.11
  script:
    - pip install langlint
    - langlint scan . -o report.json --format json
    - |
      if [ -s report.json ]; then
        echo "⚠️ Found translatable content"
        cat report.json
      fi
  artifacts:
    paths:
      - report.json
    expire_in: 1 week

langlint-translate:
  stage: translate
  image: python:3.11
  only:
    - main
  script:
    - pip install langlint
    - langlint translate src/ -o src_en/
  artifacts:
    paths:
      - src_en/
    expire_in: 1 month
```

### Azure Pipelines Integration

Add to `azure-pipelines.yml`:

```yaml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
  displayName: 'Use Python 3.11'

- script: |
    pip install langlint
  displayName: 'Install LangLint (Rust-powered!)'

- script: |
    langlint scan . -o $(Build.ArtifactStagingDirectory)/report.json --format json
  displayName: 'Scan translatable content'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(Build.ArtifactStagingDirectory)'
    artifactName: 'langlint-report'
```

### Docker Integration

#### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install LangLint (Rust-powered!)
RUN pip install --no-cache-dir langlint

# Copy source code
COPY . .

# Run translation (now 10x faster!)
CMD ["langlint", "translate", ".", "-t", "google", "-s", "zh-CN", "-l", "en", "-o", "output/"]
```

#### Use Docker Compose

```yaml
version: '3.8'

services:
  langlint:
    image: python:3.11-slim
    volumes:
      - .:/app
    working_dir: /app
    command: >
      sh -c "
        pip install langlint &&
        langlint translate src/ -o src_en/
      "
```

### VS Code Integration (Coming Soon)

Upcoming VS Code extension will provide:
- ✅ Real-time translation suggestions
- ✅ Right-click menu translation
- ✅ Auto-translate on save
- ✅ Translation status indicator

### Best Practices

#### 1️⃣ Keep LangLint Updated for Maximum Coverage

```bash
# For pipx users (recommended)
pipx upgrade langlint

# For uv users
uv tool upgrade langlint

# For pip users
pip install --upgrade langlint
```

> **Why stay updated?** LangLint continuously improves language detection accuracy, adds new file type support, and fixes edge cases. Regular updates ensure the best translation quality.

#### 2️⃣ Phased Integration

```bash
# Phase 1: Scan only, don't block CI
langlint scan . -o report.json --format json

# Phase 2: Generate warnings
if grep -qE '"(zh-CN|zh-TW|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi)"' report.json; then
  echo "⚠️ Warning: Found non-English content"
  grep -oE '"(zh-CN|zh-TW|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi)"' report.json | sort -u
fi

# Phase 3: Block commits (strict mode)
if grep -qE '"(zh-CN|zh-TW|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi)"' report.json; then
  echo "❌ Error: Non-English content found. Must translate before merging"
  grep -oE '"(zh-CN|zh-TW|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi)"' report.json | sort -u
  exit 1
fi
```

#### 3️⃣ Translate Only New Content

```bash
# Get changed files (handles filenames with spaces)
git diff -z --name-only origin/main... | xargs -0 langlint fix

# Or using a loop for more control
git diff --name-only origin/main... | while IFS= read -r file; do
  langlint fix "$file"
done
```

#### 4️⃣ Cache Optimization

```yaml
# Enable cache in GitHub Actions
- name: Cache LangLint
  uses: actions/cache@v3
  with:
    path: ~/.cache/langlint
    key: ${{ runner.os }}-langlint-${{ hashFiles('**/*.py') }}
    restore-keys: |
      ${{ runner.os }}-langlint-
```

### Enterprise Deployment

#### Self-hosted Runner

```yaml
jobs:
  translate:
    runs-on: [self-hosted, linux, x64]
    steps:
      - name: Translate with Google Translate
        run: |
          langlint translate src/ -s zh-CN -t en --translator google -o src_en/

```


Through CI/CD integration, LangLint can become an indispensable part of your development workflow, just like Ruff, automating multilingual code translation and improving team collaboration efficiency!

</details>

## 🛠️ Development

### Building from Source

```bash
# Prerequisites
# 1. Install Rust (https://rustup.rs/)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Install Python 3.8+
python --version

# 3. Install maturin (Rust-Python build tool)
pip install maturin

# Build and install locally
maturin develop --release

# Run Rust tests
cargo test --workspace --exclude langlint_py

# Run Python tests
pytest tests/ --cov=python_wrapper/langlint --cov-report=term-missing

# Run ignored tests (Google API - requires network)
cargo test --workspace --exclude langlint_py -- --ignored
```

### 🧪 Testing

```bash
# Run Rust tests
cargo test --workspace --exclude langlint_py

# Run Python tests
pytest tests/ -v

# Run all tests with coverage
pytest tests/ --cov=python_wrapper/langlint --cov-report=term-missing
```

### Contributing

```bash
# 1. Clone the repository
git clone https://github.com/HzaCode/Langlint.git
cd Langlint

# 2. Install dependencies
cargo build

# 3. Make your changes in crates/

# 4. Run tests
cargo test
cargo clippy  # Linting
cargo fmt     # Formatting

# 5. Build Python package
maturin develop --release

# 6. Test Python integration
python -c "import langlint_py; print(langlint_py.version())"
```

## 🤝 Contributing

Contributions welcome! The codebase is now **100% Rust** for maximum performance.

**How to contribute:**

1. **Core features**: Add to `crates/langlint_*`
2. **New parsers**: Extend `crates/langlint_parsers/src/`
3. **New translators**: Add to `crates/langlint_translators/src/`
4. **Python API**: Update `crates/langlint_py/src/lib.rs`

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🔒 Privacy

LangLint respects your privacy. We follow a **local-first** approach:
- ✅ No telemetry, tracking, or analytics
- ✅ Your code stays on your machine
- ✅ Translation data only sent to APIs you explicitly choose to use

For complete details, see our [Privacy Policy](PRIVACY.md).

## 📞 Contact & Links

- **Homepage**: [https://github.com/HzaCode/Langlint](https://github.com/HzaCode/Langlint)
- **PyPI**: [https://pypi.org/project/langlint/](https://pypi.org/project/langlint/)
- **Issues**: [https://github.com/HzaCode/Langlint/issues](https://github.com/HzaCode/Langlint/issues)
- **Discussions**: [https://github.com/HzaCode/Langlint/discussions](https://github.com/HzaCode/Langlint/discussions)

---

<div align="center">

**Made with ❤️ and 🦀 (Rust)**

**10-50x faster than pure Python** ⚡

[⭐ Star us on GitHub](https://github.com/HzaCode/Langlint) | [📦 Install from PyPI](https://pypi.org/project/langlint/) | [🦀 View Rust Code](https://github.com/HzaCode/Langlint/tree/main/crates)

⭐ **LLM too slow? Try LangLint!** Now powered by Rust for maximum speed 🚀

</div>
