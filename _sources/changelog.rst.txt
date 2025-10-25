Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[1.0.0] - 2025-01-01
--------------------

Initial Release
~~~~~~~~~~~~~~~

Added
^^^^^

* 🎉 First stable release of LangLint v1.0.0
* 🔌 Pluggable parser architecture supporting multiple file types
* 🌐 Multi-translator support (Google Translate, Mock)
* ⚡ High-performance Rust implementation (10-50× faster)
* 🛠️ Comprehensive configuration system
* 📊 Complete test suite (44 tests, all passing)
* 📚 Full documentation with Read the Docs
* 🚀 CLI interface with three main commands: scan, translate, fix
* 🔒 Privacy-focused design with no telemetry
* 📦 PyPI package distribution

Features
^^^^^^^^

**File Type Support (28+):**
  * Python (``.py``)
  * JavaScript/TypeScript (``.js``, ``.ts``, ``.jsx``, ``.tsx``)
  * Rust (``.rs``)
  * Go (``.go``)
  * C/C++ (``.c``, ``.cpp``, ``.h``)
  * Java, Kotlin, Scala
  * Markdown (``.md``)
  * Jupyter Notebooks (``.ipynb``)
  * And many more...

**Translation Services:**
  * Google Translate (free, no API key required)
  * Mock translator (for testing)

**Performance:**
  * Rust-powered core
  * True multi-threading
  * 10-50× faster than Python implementation
  * Efficient memory management

**Quality:**
  * 44 passing tests
  * Comprehensive error handling
  * Automatic backup creation
  * Dry-run mode for safety

Technical Details
^^^^^^^^^^^^^^^^^

* Python 3.8+ support
* Async/await support
* Type annotations
* Cross-platform compatibility
* CI/CD with GitHub Actions

Documentation
^^^^^^^^^^^^^

* README.md - Project introduction
* CITATION.cff - Citation information
* Complete API documentation
* Tutorials and examples
* Contributing guide

Future Plans
------------

Upcoming Features
~~~~~~~~~~~~~~~~~

* OpenAI GPT translator (Rust implementation)
* DeepL translator (Rust implementation)
* Azure Translator support (Rust implementation)
* VS Code extension
* More language support
* Performance benchmarks
* Improved caching
* Performance optimizations

Version History
---------------

* **1.0.0** (2025-01-01) - Initial stable release

Support Policy
--------------

* **Current version**: Full support (features + bug fixes)
* **Previous major version**: Bug fixes only
* **Older versions**: No longer supported

Upgrade Guide
-------------

Major Version Upgrades
~~~~~~~~~~~~~~~~~~~~~~

When upgrading between major versions, check the upgrade guide for breaking changes.

Minor Version Upgrades
~~~~~~~~~~~~~~~~~~~~~~

Minor version upgrades are backward compatible and can be installed directly.

Patch Version Upgrades
~~~~~~~~~~~~~~~~~~~~~~

Patch versions contain bug fixes and should be installed immediately.

Contributors
------------

Thank you to all contributors who have helped make LangLint better!

Core Team
~~~~~~~~~

* Zhiang He - Project maintainer

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.

Links
-----

* `Project Homepage <https://github.com/HzaCode/Langlint>`_
* `Documentation <https://langlint.readthedocs.io>`_
* `Issue Tracker <https://github.com/HzaCode/Langlint/issues>`_
* `Discussions <https://github.com/HzaCode/Langlint/discussions>`_
* `PyPI Package <https://pypi.org/project/langlint/>`_

