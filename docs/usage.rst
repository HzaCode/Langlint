Usage Guide
===========

This guide covers the main features and usage patterns of LangLint.

Supported Languages
-------------------

LangLint supports 100+ language pairs, including:

European Languages
~~~~~~~~~~~~~~~~~~

* English (en)
* French (fr)
* German (de)
* Spanish (es)
* Italian (it)
* Portuguese (pt)
* Russian (ru)
* Dutch (nl)
* Polish (pl)
* Swedish (sv)

Asian Languages
~~~~~~~~~~~~~~~

* Simplified Chinese (zh-CN)
* Traditional Chinese (zh-TW)
* Japanese (ja)
* Korean (ko)
* Thai (th)
* Vietnamese (vi)
* Hindi (hi)
* Indonesian (id)

Other Languages
~~~~~~~~~~~~~~~

* Arabic (ar)
* Hebrew (he)
* Turkish (tr)
* Greek (el)
* Persian (fa)

Supported File Types
--------------------

LangLint supports 28+ file types:

Programming Languages
~~~~~~~~~~~~~~~~~~~~~

* **Python**: ``.py``
* **JavaScript/TypeScript**: ``.js``, ``.ts``, ``.jsx``, ``.tsx``
* **Rust**: ``.rs``
* **Go**: ``.go``
* **C/C++**: ``.c``, ``.cpp``, ``.h``, ``.hpp``
* **Java**: ``.java``
* **Kotlin**: ``.kt``
* **Scala**: ``.scala``
* **C#**: ``.cs``
* **PHP**: ``.php``
* **Ruby**: ``.rb``
* **Swift**: ``.swift``
* **Dart**: ``.dart``
* **Lua**: ``.lua``

Documentation & Data
~~~~~~~~~~~~~~~~~~~~

* **Markdown**: ``.md``
* **Jupyter Notebooks**: ``.ipynb``
* **Shell Scripts**: ``.sh``, ``.bash``
* **SQL**: ``.sql``
* **R**: ``.r``, ``.R``
* **MATLAB**: ``.m``
* **Vim Script**: ``.vim``

What Gets Translated
--------------------

LangLint intelligently translates:

✅ **Translated**:
  * Comments (``# inline comments``)
  * Docstrings (``"""docstring"""``)
  * Documentation strings
  * Markdown text content

❌ **Not Translated** (Preserved):
  * Variable names
  * Function names
  * String literals
  * Code syntax
  * Import statements
  * Configuration values

Command Options
---------------

scan Command
~~~~~~~~~~~~

.. code-block:: bash

   langlint scan [OPTIONS] PATH

Options:

* ``-o, --output FILE`` - Save results to file
* ``--format FORMAT`` - Output format (json/yaml/csv)
* ``-i, --include PATTERN`` - Include file patterns
* ``-e, --exclude PATTERN`` - Exclude file patterns
* ``-v, --verbose`` - Enable verbose output

Examples:

.. code-block:: bash

   # Scan with JSON output
   langlint scan src/ -o report.json --format json

   # Scan with exclusions
   langlint scan . -e "**/test_*" -e "**/__pycache__/"

translate Command
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   langlint translate [OPTIONS] PATH

Options:

* ``-s, --source-lang LANG`` - Source language code (default: auto)
* ``-t, --target-lang LANG`` - Target language code (default: en)
* ``--translator SERVICE`` - Translation service (google/mock, default: google)
* ``-o, --output DIR`` - Output directory
* ``--dry-run`` - Preview without making changes
* ``-i, --include PATTERN`` - Include patterns
* ``-e, --exclude PATTERN`` - Exclude patterns

Examples:

.. code-block:: bash

   # Basic translation
   langlint translate src/ -s zh-CN -t en -o output/

   # Dry run
   langlint translate src/ -s zh-CN -t en --dry-run

   # With specific translator (google or mock only)
   langlint translate src/ --translator google

fix Command
~~~~~~~~~~~

.. code-block:: bash

   langlint fix [OPTIONS] PATH

Options:

* ``-s, --source-lang LANG`` - Source language code (default: auto)
* ``-t, --target-lang LANG`` - Target language code (default: en)
* ``--translator SERVICE`` - Translation service (default: google)
* ``-i, --include PATTERN`` - Include patterns
* ``-e, --exclude PATTERN`` - Exclude patterns

Examples:

.. code-block:: bash

   # Basic fix
   langlint fix src/ -s zh-CN -t en

   # With specific translator (google or mock only)
   langlint fix src/ -s zh-CN -t en --translator google

Advanced Usage
--------------

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple files efficiently:

.. code-block:: bash

   # Translate all Python files
   langlint fix **/*.py -s zh-CN -t en

   # Translate specific directories
   langlint fix src/ tests/ docs/ -s zh-CN -t en

Language Detection
~~~~~~~~~~~~~~~~~~

LangLint can auto-detect languages, but explicit specification is more accurate:

.. code-block:: bash

   # Auto-detect (may misidentify European languages)
   langlint fix file.py -s auto -t en

   # Explicit source (recommended for European languages)
   langlint fix french_file.py -s fr -t en

Custom Exclusions
~~~~~~~~~~~~~~~~~

Exclude specific files or directories:

.. code-block:: bash

   # Exclude test files
   langlint scan src/ -e "**/test_*"

   # Multiple exclusions
   langlint scan . -e "**/node_modules/**" -e "**/__pycache__/**"

Python API
----------

LangLint can be used as a Python library:

.. code-block:: python

   import langlint_py

   # Scan files
   result = langlint_py.scan(
       "src/",
       format="json",
       verbose=True
   )
   print(result)

   # Translate files
   result = langlint_py.translate(
       "example.py",
       source="zh-CN",
       target="en",
       translator="google",
       output="example_en.py",
       dry_run=False
   )
   print(result)

Best Practices
--------------

1. **Always specify source language** for European languages (French, German, Spanish, etc.)
2. **Use dry-run first** to preview changes
3. **Backup important files** before in-place translation
4. **Test translated code** to ensure it still works
5. **Use configuration files** for consistent settings across teams

Troubleshooting
---------------

File Not Translated
~~~~~~~~~~~~~~~~~~~

If a file is not being translated:

1. Check if the file type is supported
2. Verify the file contains translatable content
3. Check exclusion patterns in your config
4. Run with ``--verbose`` to see detailed output

Translation Quality
~~~~~~~~~~~~~~~~~~~

To improve translation quality:

1. Use explicit source language (``-s fr`` instead of ``-s auto``)
2. Consider using different translators
3. Review and manually adjust complex technical terms
4. Maintain a glossary for domain-specific terms

Performance Tips
~~~~~~~~~~~~~~~~

For large projects:

1. Use configuration file to set default options
2. Enable caching (enabled by default)
3. Process files in batches
4. Use exclusion patterns to skip unnecessary files

