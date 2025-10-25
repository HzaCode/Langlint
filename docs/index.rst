LangLint Documentation
======================

**LangLint** is a high-performance, extensible, **Rust-powered, code-aware translation and linting toolkit** for code comments and documentation. It keeps multilingual scientific software docs consistent and reproducible, supporting **FAIR** and open-science practices.

.. image:: https://img.shields.io/pypi/v/langlint.svg
   :target: https://pypi.org/project/langlint/
   :alt: PyPI

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
   :target: https://www.python.org/
   :alt: Python

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/badge/rust-1.90%2B-orange.svg
   :target: https://www.rust-lang.org/
   :alt: Rust

.. image:: https://github.com/HzaCode/Langlint/workflows/CI/badge.svg
   :target: https://github.com/HzaCode/Langlint/actions
   :alt: CI

.. image:: https://codecov.io/gh/HzaCode/Langlint/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/HzaCode/Langlint
   :alt: codecov

.. image:: https://static.pepy.tech/badge/langlint?style=flat-square
   :target: https://pepy.tech/project/langlint
   :alt: Downloads

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install via pip
   pip install langlint

   # Or use pipx for isolated environment
   pipx install langlint

   # Or use uv for fastest installation
   uv tool install langlint

Basic Usage
~~~~~~~~~~~

.. code-block:: bash

   # Scan translatable content
   langlint scan src/

   # Translate (preserve original files)
   langlint translate src/ -s zh-CN -t en -o output/

   # In-place translation (auto backup)
   langlint fix src/ -s zh-CN -t en

Features
--------

* 🌍 **100+ Language Pairs**: Support for major world languages
* ⚡ **High Performance**: 10-50× faster with Rust implementation
* 🔌 **28+ File Types**: Python, JavaScript, Rust, Markdown, Jupyter, and more
* 🔒 **Syntax Protection**: Automatically excludes string literals
* 🚀 **Batch Processing**: True parallelism with Rust
* 🆓 **Free Translation**: Google Translate, no API key required

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   usage
   configuration
   cli

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/parsers
   api/translators

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

.. toctree::
   :maxdepth: 1
   :caption: About

   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

