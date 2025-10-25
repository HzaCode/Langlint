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
   langlint translate src/ -s auto -t en -o output/

   # In-place translation (auto backup)
   langlint fix src/ -s auto -t en

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

