# LangLint

> **Breaking Language Barriers in Research Collaboration** 🚀 | As Fast as Ruff, Integrate into Your CI/CD Pipeline

[![PyPI](https://badge.fury.io/py/langlint.svg)](https://badge.fury.io/py/langlint)
[![Python](https://img.shields.io/pypi/pyversions/langlint.svg)](https://pypi.org/project/langlint/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LangLint** is an extensible automated translation and standardization platform designed to eliminate language barriers in structured text for research collaboration.

## 🚀 Quick Start

```bash
# Install
pip install langlint

# Scan translatable content
langlint scan src/

# Translate (preserve original files)
langlint translate src/ -o output/

# In-place translation (auto backup)
langlint fix src/
```

### Core Commands

| Command | Function | Example |
|---------|----------|---------|
| `scan` | Scan translatable content | `langlint scan .` |
| `translate` | Translate to new directory | `langlint translate . -o output/` |
| `fix` | In-place translate + backup | `langlint fix .` |

**Default: Google Translate, Auto-detect → English** (Free, no API Key required)

<details>
<summary>Other Translators (OpenAI, DeepL, Azure)</summary>

- `openai` - OpenAI GPT (requires `OPENAI_API_KEY`)
- `deepl` - DeepL (requires `DEEPL_API_KEY`)
- `azure` - Azure Translator (requires `AZURE_API_KEY`)

</details>

## ✨ Key Features

### 🌍 Multilingual Translation Support

- ✅ **100+ Language Pairs**: French↔English, German↔Chinese, Spanish↔Japanese, etc.
- ✅ **Smart Language Detection**: Auto-detect source language or specify manually
- ✅ **Syntax Protection**: Automatically excludes string literals and f-strings
- ✅ **High-Performance Concurrency**: Batch translation for multiple files

```bash
# Basic usage (auto-detect → English)
langlint fix src/

# European languages (French → English, specify source to avoid misdetection)
langlint fix french_code.py -s fr

# Translate to other languages (German → Chinese)
langlint fix german_code.py -s de -l zh-CN
```

<details>
<summary>📋 Supported Languages List</summary>

**European Languages**: English (en), French (fr), German (de), Spanish (es), Italian (it), Portuguese (pt), Russian (ru), Dutch (nl), Polish (pl), Swedish (sv)

**Asian Languages**: Simplified Chinese (zh-CN), Traditional Chinese (zh-TW), Japanese (ja), Korean (ko), Thai (th), Vietnamese (vi), Hindi (hi), Indonesian (id)

**Other Languages**: Arabic (ar), Hebrew (he), Turkish (tr), Greek (el), Persian (fa)

**Note**: European languages (French, German, Spanish, Italian, etc.) **must** use the `-s` parameter to specify source language, otherwise they will be misidentified as English!

</details>

### 🔌 Supported File Types
Python • Markdown • Jupyter Notebook • JavaScript/TypeScript • Go • Rust • Java • C/C++ • Config files (YAML/TOML/JSON) • 20+ types

### ⚡ High Performance
Concurrent processing is **10-20x faster** than serial 🚀

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
# Scenario 1: Translate French project to English
langlint scan french_project/ -o report.json --format json
langlint translate french_project/ -s fr -o english_project/

# Scenario 2: Generate multilingual documentation
langlint translate docs/ -s en -l zh-CN -o docs_zh/
langlint translate docs/ -s en -l ja -o docs_ja/
langlint translate docs/ -s en -l fr -o docs_fr/

# Scenario 3: Internationalize codebase
langlint fix src/
pytest tests/  # Verify functionality
```

### Advanced Parameters

```bash
# Exclude specific files
langlint translate src/ -o output/ -e "**/test_*" -e "**/__pycache__/"

# Dry-run preview
langlint translate src/ -s fr --dry-run

# Use other translators
langlint translate src/ -t openai  # Requires OPENAI_API_KEY
langlint translate src/ -t deepl   # Requires DEEPL_API_KEY
```

</details>

<details>
<summary>🔧 Low-Level API Usage (Click to expand)</summary>

LangLint can be used as a Python library in your projects.

#### Basic API Usage

```python
import asyncio
from langlint.core.client import Dispatcher
from langlint.translators.google_translator import GoogleTranslator, GoogleConfig
from langlint.core.types import TranslatableUnit, UnitType
from pathlib import Path

async def translate_file_example():
    """Example of translating a single file"""
    
    # 1. Create translator
    config = GoogleConfig(
        delay_range=(0.3, 0.6),  # Delay 0.3-0.6s per request to avoid rate limits
        timeout=30,
        retry_count=3
    )
    translator = GoogleTranslator(config)
    
    # 2. Create dispatcher
    dispatcher = Dispatcher()
    
    # 3. Parse file
    file_path = Path("example.py")
    result = await dispatcher.parse_file(str(file_path))
    
    if result.success:
        # 4. Translate extracted units
        source_lang = "fr"  # French
        target_lang = "en"  # English
        
        texts = [unit.content for unit in result.units]
        translation_results = await translator.translate_batch(
            texts, 
            source_lang, 
            target_lang
        )
        
        # 5. Create translated units
        translated_units = []
        for unit, trans_result in zip(result.units, translation_results):
            translated_unit = TranslatableUnit(
                content=trans_result.translated_text,
                unit_type=unit.unit_type,
                line_number=unit.line_number,
                column_number=unit.column_number,
                context=unit.context
            )
            translated_units.append(translated_unit)
        
        # 6. Reconstruct file
        original_content = file_path.read_text(encoding='utf-8')
        reconstructed = result.parser.reconstruct_file(
            original_content, 
            translated_units, 
            str(file_path)
        )
        
        # 7. Write output
        output_path = Path("example_translated.py")
        output_path.write_text(reconstructed, encoding='utf-8')
        
        print(f"Translation completed: {output_path}")

# Run example
asyncio.run(translate_file_example())
```

#### Batch Translate Multiple Files

```python
import asyncio
from pathlib import Path
from langlint.core.client import Dispatcher
from langlint.translators.google_translator import GoogleTranslator, GoogleConfig

async def batch_translate_project(
    source_dir: str, 
    output_dir: str, 
    source_lang: str = "zh-CN",
    target_lang: str = "en"
):
    """Batch translate project files"""
    
    translator = GoogleTranslator(GoogleConfig())
    dispatcher = Dispatcher()
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all Python files
    py_files = list(source_path.rglob("*.py"))
    
    print(f"Found {len(py_files)} Python files")
    
    for file_path in py_files:
        try:
            print(f"Translating: {file_path}")
            
            # Parse file
            result = await dispatcher.parse_file(str(file_path))
            
            if not result.success or not result.units:
                print(f"  Skipped (no translatable content)")
                continue
            
            # Translate
            texts = [unit.content for unit in result.units]
            translations = await translator.translate_batch(
                texts, source_lang, target_lang
            )
            
            # Reconstruct
            translated_units = [
                unit._replace(content=trans.translated_text)
                for unit, trans in zip(result.units, translations)
            ]
            
            original = file_path.read_text(encoding='utf-8')
            reconstructed = result.parser.reconstruct_file(
                original, translated_units, str(file_path)
            )
            
            # Save
            relative = file_path.relative_to(source_path)
            out_file = output_path / relative
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(reconstructed, encoding='utf-8')
            
            print(f"  ✓ Completed")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")

# Usage example
asyncio.run(batch_translate_project(
    "src/",           # Source directory
    "src_en/",        # Output directory
    "fr",             # French
    "en"              # English
))
```

#### Custom Translator

```python
from langlint.translators.base import Translator, TranslationResult, TranslationStatus
from typing import List

class CustomTranslator(Translator):
    """Custom translator example"""
    
    def __init__(self, api_key: str):
        super().__init__(name="custom")
        self.api_key = api_key
    
    async def translate(
        self, 
        text: str, 
        source_language: str, 
        target_language: str
    ) -> TranslationResult:
        """Single text translation"""
        # Implement your translation logic
        translated = await self._call_your_api(text, source_language, target_language)
        
        return TranslationResult(
            original_text=text,
            translated_text=translated,
            source_language=source_language,
            target_language=target_language,
            status=TranslationStatus.SUCCESS,
            confidence=0.9,
            metadata={"translator": "custom"}
        )
    
    async def translate_batch(
        self, 
        texts: List[str], 
        source_language: str, 
        target_language: str
    ) -> List[TranslationResult]:
        """Batch translation"""
        # Use concurrency for efficiency
        import asyncio
        tasks = [
            self.translate(text, source_language, target_language) 
            for text in texts
        ]
        return await asyncio.gather(*tasks)
    
    async def _call_your_api(self, text, source, target):
        """Call your translation API"""
        # Implement API call logic
        pass
```

#### 🎯 Best Practices

**1. Performance Optimization**

```python
# ✅ Recommended: Use batch translation
texts = ["text1", "text2", "text3"]
results = await translator.translate_batch(texts, "zh-CN", "en")

# ❌ Avoid: Translate one by one (slow)
for text in texts:
    result = await translator.translate(text, "zh-CN", "en")
```

**2. Error Handling**

```python
try:
    result = await translator.translate(text, source_lang, target_lang)
    if result.status == TranslationStatus.SUCCESS:
        print(f"Translation succeeded: {result.translated_text}")
    else:
        print(f"Translation failed: {result.metadata.get('error')}")
except Exception as e:
    print(f"Exception: {e}")
```

**3. Rate Limit Management**

```python
# Google Translate limit: ~5 requests/sec
config = GoogleConfig(
    delay_range=(0.3, 0.6),  # Delay per request to avoid limits
    retry_count=3,            # Retry attempts on failure
    timeout=30                # Timeout duration
)
translator = GoogleTranslator(config)
```

**4. Concurrency Control**

```python
import asyncio

# Use Semaphore to control concurrency
sem = asyncio.Semaphore(5)  # Max 5 concurrent requests

async def translate_with_limit(text):
    async with sem:
        return await translator.translate(text, "fr", "en")

tasks = [translate_with_limit(t) for t in texts]
results = await asyncio.gather(*tasks)
```

**5. Language Code Standards**

```python
# ✅ Recommended: Use standard language codes
"zh-CN"  # Simplified Chinese
"zh-TW"  # Traditional Chinese
"en"     # English
"fr"     # French
"de"     # German
"es"     # Spanish
"ja"     # Japanese
"ko"     # Korean

# ❌ Avoid: Non-standard codes
"zh"     # Will be auto-converted to zh-CN, but better to specify
"chinese" # Not supported
```

</details>

<details>
<summary>⚙️ Configuration File (Click to expand)</summary>

Configure in `pyproject.toml`:

```toml
[tool.langlint]
translator = "google"
target_lang = "en"
source_lang = ["zh-CN", "ja", "ko"]
exclude = ["**/test_*", "**/data/"]

# Path-specific settings
[tool.langlint."docs/**/*.md"]
translator = "deepl"
```

</details>

## 🤖 CI/CD Integration

**Integrate into Your Workflow Like Ruff** - Automate multilingual code checking and translation!

Supports: GitHub Actions ✅ | GitLab CI ✅ | Azure Pipelines ✅ | Pre-commit Hooks ✅ | Docker ✅

### 🎯 Best Practice: Use with Ruff

```bash
# First, check code quality with Ruff
ruff check . --fix

# Then, translate with LangLint (auto-detects non-English, translates to English)
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

jobs:
  langlint-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install LangLint
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
    - cron: '0 0 * * 0'  # Run every Sunday

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
      
      - name: Install LangLint
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
      
      - name: Install LangLint
        run: pip install langlint
      
      - name: Check for non-English content
        run: |
          # Scan for Chinese content
          langlint scan . -o report.json --format json
          
          # Fail if Chinese content found
          if grep -q '"zh-CN"' report.json; then
            echo "❌ Found Chinese content. Please translate before committing."
            echo "Run: langlint fix ."
            exit 1
          fi
          
          echo "✅ All content is in English."
```

#### 4️⃣ Multilingual Documentation Auto-Publish

Automatically translate documentation to multiple languages:

```yaml
name: Translate Docs

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'

jobs:
  translate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install LangLint
        run: pip install langlint
      
      - name: Translate to multiple languages
        run: |
          # Translate to Chinese
          langlint translate docs/ -s en -l zh-CN -o docs_zh/
          
          # Translate to Japanese
          langlint translate docs/ -s en -l ja -o docs_ja/
          
          # Translate to French
          langlint translate docs/ -s en -l fr -o docs_fr/
          
          # Translate to Spanish
          langlint translate docs/ -s en -l es -o docs_es/
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./
          keep_files: true
```

### Pre-commit Hooks Integration

Like Ruff, add LangLint to your pre-commit configuration.

#### Install pre-commit

```bash
pip install pre-commit
```

#### Configure `.pre-commit-config.yaml`

```yaml
repos:
  # LangLint - Check translatable content
  - repo: local
    hooks:
      - id: langlint-scan
        name: LangLint Scan
        entry: langlint scan
        language: system
        types: [python, markdown]
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
  displayName: 'Install LangLint'

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

# Install LangLint
RUN pip install --no-cache-dir langlint

# Copy source code
COPY . .

# Run translation
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

#### 1️⃣ Phased Integration

```bash
# Phase 1: Scan only, don't block CI
langlint scan . -o report.json --format json

# Phase 2: Generate warnings
if grep -q '"zh-CN"' report.json; then
  echo "⚠️ Warning: Found translatable content"
fi

# Phase 3: Block commits (strict mode)
if grep -q '"zh-CN"' report.json; then
  echo "❌ Error: Must translate before merging"
  exit 1
fi
```

#### 2️⃣ Translate Only New Content

```bash
# Get changed files
git diff --name-only origin/main... > changed_files.txt

# Translate only changed files
cat changed_files.txt | xargs langlint fix
```

#### 3️⃣ Cache Optimization

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
      - name: Translate with enterprise translator
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          langlint translate src/ -t openai -o src_en/
```

#### Secrets Management

```yaml
# Configure in GitHub Secrets
# Settings > Secrets and variables > Actions > New repository secret

env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
```

Through CI/CD integration, LangLint can become an indispensable part of your development workflow, just like Ruff, automating multilingual code translation and improving team collaboration efficiency!

</details>

## 🤝 Contributing

Contributions welcome! See the [Contributing Guide](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Homepage**: https://github.com/HzaCode/Langlint
- **Issue Tracker**: https://github.com/HzaCode/Langlint/issues
- **Discussions**: https://github.com/HzaCode/Langlint/discussions

---

⭐ If you find this useful, please give the project a Star!
