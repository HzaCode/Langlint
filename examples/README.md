# LangLint Examples

This directory contains end-to-end examples demonstrating LangLint's capabilities across different use cases.

## 📚 Available Examples

### 1. Basic Usage (`basic/`)
Simple examples to get started with LangLint.

### 2. Python Translation (`python_translation/`)
Translate Python code comments and docstrings from various languages to English.

### 3. Jupyter Notebook (`jupyter_notebook/`)
Translate Jupyter notebook markdown cells and code comments.

## 🚀 Quick Start

### Example 1: Translate Python File

```bash
cd examples/python_translation
langlint scan example.py
langlint translate example.py -s auto -t en -o translated/
```

### Example 2: Translate Jupyter Notebook

```bash
cd examples/jupyter_notebook
langlint translate notebook.ipynb -s zh-CN -t en -o translated/
```

## 📖 Documentation

For more details, see:
- [Quick Start Guide](../README.md#quick-start)
- [CLI Documentation](../README.md#core-commands)
- [Configuration Guide](../README.md#configuration-file)

## 🤝 Contributing

Have a great example? Please contribute! See [CONTRIBUTING.md](../CONTRIBUTING.md).

