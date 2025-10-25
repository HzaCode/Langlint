Configuration
=============

LangLint can be configured using a ``.langlint.yml`` file in your project root.

Configuration File
------------------

Create ``.langlint.yml`` in your project root:

.. code-block:: yaml

   # Global settings
   translator: "google"  # google (default, free) or mock (testing)
   target_lang: "en"
   source_lang: ["zh-CN", "ja", "ko"]
   backup: true  # Create backup files before in-place translation

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

Configuration Options
---------------------

Global Settings
~~~~~~~~~~~~~~~

translator
^^^^^^^^^^

Translation service to use.

* Type: string
* Default: ``"google"``
* Options: ``"google"`` (free), ``"mock"`` (testing only)

Example:

.. code-block:: yaml

   translator: "google"  # or "mock" for testing

target_lang
^^^^^^^^^^^

Target language for translation.

* Type: string
* Default: ``"en"``
* Format: ISO 639-1 language code

Example:

.. code-block:: yaml

   target_lang: "en"  # English
   # or
   target_lang: "zh-CN"  # Simplified Chinese

source_lang
^^^^^^^^^^^

Source languages to detect and translate.

* Type: list of strings
* Default: ``["zh-CN", "ja", "ko"]``
* Format: List of ISO 639-1 language codes

Example:

.. code-block:: yaml

   source_lang: ["zh-CN", "ja", "ko"]
   # or
   source_lang: ["fr", "de", "es"]  # European languages

backup
^^^^^^

Create backup files before in-place translation.

* Type: boolean
* Default: ``true``

Example:

.. code-block:: yaml

   backup: true  # Creates .backup files
   # or
   backup: false  # No backups

File Processing
~~~~~~~~~~~~~~~

include
^^^^^^^

File patterns to include.

* Type: list of strings
* Default: ``["**/*.py", "**/*.md", "**/*.ipynb"]``
* Format: Glob patterns

Example:

.. code-block:: yaml

   include:
     - "**/*.py"
     - "**/*.js"
     - "**/*.ts"
     - "**/*.md"

exclude
^^^^^^^

File patterns to exclude.

* Type: list of strings
* Default: ``["**/node_modules/**", "**/__pycache__/**", "**/.git/**"]``
* Format: Glob patterns

Example:

.. code-block:: yaml

   exclude:
     - "**/node_modules/**"
     - "**/test_*"
     - "**/.venv/**"
     - "**/build/**"

Path-Specific Overrides
~~~~~~~~~~~~~~~~~~~~~~~

Override settings for specific paths:

.. code-block:: yaml

   path_configs:
     # Use mock translator for tests
     "**/tests/**":
       translator: "mock"
       backup: false

     # Different target for docs
     "**/docs/**":
       target_lang: "zh-CN"

     # Skip data directories
     "**/data/**":
       exclude: true

Command-Line Overrides
----------------------

Command-line options override configuration file settings:

.. code-block:: bash

   # Config says target_lang: "en", but CLI overrides to "zh"
   langlint fix src/ --target-lang zh

Priority order (highest to lowest):

1. Command-line options
2. Configuration file
3. Default values

Backup Control
--------------

The ``backup`` option controls automatic backup creation:

Configuration file:

.. code-block:: yaml

   backup: true

Command-line override:

.. code-block:: bash

   # Disable backup (overrides config)
   langlint fix src/ -s zh-CN -t en --no-backup

Backup files are created with ``.backup`` extension:

.. code-block:: text

   example.py         # Translated file
   example.py.backup  # Original backup

Environment Variables
---------------------

Currently supported translators do not require environment variables:

Google Translate
~~~~~~~~~~~~~~~~

No API key or environment variables needed (free service).

Mock Translator
~~~~~~~~~~~~~~~

No configuration needed (for testing only).

Configuration Examples
----------------------

Minimal Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   translator: "google"
   target_lang: "en"

Full Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Global settings
   translator: "google"
   target_lang: "en"
   source_lang: ["zh-CN", "ja", "ko", "fr", "de"]
   backup: true

   # File processing
   include:
     - "**/*.py"
     - "**/*.js"
     - "**/*.ts"
     - "**/*.md"
     - "**/*.ipynb"

   exclude:
     - "**/node_modules/**"
     - "**/test_*"
     - "**/__pycache__/**"
     - "**/.git/**"
     - "**/build/**"
     - "**/dist/**"

   # Path-specific overrides
   path_configs:
     "**/tests/**":
       translator: "mock"
       backup: false

     "**/docs/**":
       translator: "google"
       target_lang: "en"

     "**/examples/**":
       backup: true

Multi-Project Setup
~~~~~~~~~~~~~~~~~~~

For monorepos with multiple projects:

.. code-block:: yaml

   # Root .langlint.yml
   translator: "google"
   target_lang: "en"

   path_configs:
     "frontend/**":
       source_lang: ["fr"]
       include:
         - "**/*.js"
         - "**/*.jsx"

     "backend/**":
       source_lang: ["zh-CN"]
       include:
         - "**/*.py"

     "docs/**":
       source_lang: ["ja"]
       include:
         - "**/*.md"

