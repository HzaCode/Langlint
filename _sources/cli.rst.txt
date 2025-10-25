Command-Line Interface
======================

This page documents all CLI commands and their options.

Global Options
--------------

These options work with all commands:

.. code-block:: bash

   langlint [OPTIONS] COMMAND [ARGS]

Options:

* ``--version`` - Show version and exit
* ``-v, --verbose`` - Enable verbose output
* ``-c, --config PATH`` - Path to configuration file

Commands Overview
-----------------

scan
~~~~

Scan files for translatable content without making changes.

.. code-block:: bash

   langlint scan [OPTIONS] PATH

**Arguments:**

* ``PATH`` - Path to file or directory to scan (required)

**Options:**

* ``-o, --output FILE`` - Output file for results
* ``--format FORMAT`` - Output format: ``json``, ``yaml``, or ``csv`` (default: ``json``)
* ``-i, --include PATTERN`` - Include file patterns (can be used multiple times)
* ``-e, --exclude PATTERN`` - Exclude file patterns (can be used multiple times)

**Examples:**

.. code-block:: bash

   # Scan a directory
   langlint scan src/

   # Save results to file
   langlint scan src/ -o report.json

   # Use different output format
   langlint scan src/ --format yaml -o report.yaml

   # With custom patterns
   langlint scan . -i "**/*.py" -e "**/test_*"

**Output Format (JSON):**

.. code-block:: json

   {
     "files_scanned": 10,
     "total_units": 25,
     "results": [
       {
         "file": "src/example.py",
         "units": 5
       }
     ]
   }

translate
~~~~~~~~~

Translate files to a new directory.

.. code-block:: bash

   langlint translate [OPTIONS] PATH

**Arguments:**

* ``PATH`` - Path to file or directory to translate (required)

**Options:**

* ``-s, --source-lang LANG`` - Source language code (default: ``auto``)
* ``-t, --target-lang LANG`` - Target language code (default: ``en``)
* ``--translator SERVICE`` - Translation service: ``google`` or ``mock`` (default: ``google``)
* ``-o, --output DIR`` - Output directory for translated files
* ``--dry-run`` - Show what would be translated without making changes
* ``-i, --include PATTERN`` - Include file patterns
* ``-e, --exclude PATTERN`` - Exclude file patterns

**Examples:**

.. code-block:: bash

   # Basic translation (auto-detect source language)
   langlint translate src/ -t en -o output/

   # Specify source language
   langlint translate src/ -s zh -t en -o output/

   # Dry run to preview
   langlint translate src/ -s zh -t en --dry-run

   # With exclusions
   langlint translate . -s zh -t en -o output/ -e "**/test_*"

   # Use mock translator for testing
   langlint translate src/ -s zh -t en --translator mock

fix
~~~

Translate files in-place (creates automatic backups).

.. code-block:: bash

   langlint fix [OPTIONS] PATH

**Arguments:**

* ``PATH`` - Path to file or directory to fix (required)

**Options:**

* ``-s, --source-lang LANG`` - Source language code (default: ``auto``)
* ``-t, --target-lang LANG`` - Target language code (default: ``en``)
* ``--translator SERVICE`` - Translation service: ``google`` or ``mock`` (default: ``google``)
* ``-i, --include PATTERN`` - Include file patterns
* ``-e, --exclude PATTERN`` - Exclude file patterns

**Examples:**

.. code-block:: bash

   # Basic fix (auto-detect source language)
   langlint fix src/ -t en

   # Specify source language
   langlint fix src/ -s zh -t en

   # With specific translator
   langlint fix src/ -s zh -t en --translator google

   # With custom patterns
   langlint fix . -s zh -t en -i "**/*.py" -e "**/test_*"

**Note:** The fix command will prompt for confirmation before modifying files. Backup files with ``.backup`` extension are created automatically.

Language Codes
--------------

Common Language Codes
~~~~~~~~~~~~~~~~~~~~~

European:
  * ``en`` - English
  * ``fr`` - French
  * ``de`` - German
  * ``es`` - Spanish
  * ``it`` - Italian
  * ``pt`` - Portuguese
  * ``ru`` - Russian

Asian:
  * ``zh-CN`` - Simplified Chinese
  * ``zh-TW`` - Traditional Chinese
  * ``ja`` - Japanese
  * ``ko`` - Korean
  * ``th`` - Thai
  * ``vi`` - Vietnamese
  * ``hi`` - Hindi

Other:
  * ``ar`` - Arabic
  * ``he`` - Hebrew
  * ``tr`` - Turkish

Special Values
~~~~~~~~~~~~~~

* ``auto`` - Auto-detect language (may be inaccurate for European languages)

Exit Codes
----------

LangLint uses standard exit codes:

* ``0`` - Success
* ``1`` - Error (translation failed, file not found, etc.)
* ``2`` - Usage error (invalid options, missing arguments, etc.)

Examples:

.. code-block:: bash

   # Check exit code
   langlint scan src/
   echo $?  # Prints 0 on success

   # Use in scripts
   if langlint scan src/ -o report.json; then
       echo "Scan successful"
   else
       echo "Scan failed"
   fi

Shell Integration
-----------------

Bash Completion
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Add to ~/.bashrc
   eval "$(_LANGLINT_COMPLETE=bash_source langlint)"

Zsh Completion
~~~~~~~~~~~~~~

.. code-block:: bash

   # Add to ~/.zshrc
   eval "$(_LANGLINT_COMPLETE=zsh_source langlint)"

Fish Completion
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Add to ~/.config/fish/config.fish
   eval (env _LANGLINT_COMPLETE=fish_source langlint)

