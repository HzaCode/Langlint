Quick Start
===========

This guide will help you get started with LangLint in just a few minutes.

Basic Commands
--------------

LangLint provides three main commands:

scan
~~~~

Scan files for translatable content without making changes:

.. code-block:: bash

   langlint scan path/to/files

Example output:

.. code-block:: text

   Scanning 10 files...
   Found 25 translatable units in 5 files

translate
~~~~~~~~~

Translate files to a new directory (preserves originals):

.. code-block:: bash

   langlint translate path/to/files -s auto -t en -o output/

This will:

1. Auto-detect the source language
2. Translate to English
3. Save results to the ``output/`` directory

fix
~~~

Translate files in-place (creates automatic backups):

.. code-block:: bash

   langlint fix path/to/files -s auto -t en

This will:

1. Auto-detect the source language
2. Translate to English
3. Update files in-place
4. Create ``.backup`` backup files

Simple Example
--------------

Let's translate a Python file with Chinese comments:

**Before** (``example.py``):

.. code-block:: python

   def calculate_total(items):
       """计算总价"""
       total = 0
       for item in items:
           # 累加价格
           total += item.price
       return total

**Translate**:

.. code-block:: bash

   langlint fix example.py -s zh -t en

**After**:

.. code-block:: python

   def calculate_total(items):
       """Calculate total price"""
       total = 0
       for item in items:
           # Accumulate prices
           total += item.price
       return total

Common Use Cases
----------------

Internationalize a Project
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Scan first to see what will be translated
   langlint scan src/

   # Translate all Python files
   langlint fix src/ -s zh -t en

Multi-language Support
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # French to English
   langlint fix french_code.py -s fr -t en

   # German to Chinese
   langlint fix german_code.py -s de -t zh-CN

   # Japanese to English
   langlint fix japanese_code.py -s ja -t en

Jupyter Notebooks
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Translate Jupyter notebooks
   langlint fix notebooks/ -s zh-CN -t en

Configuration File
------------------

Create a ``.langlint.yml`` file in your project root:

.. code-block:: yaml

   # Global settings
   translator: "google"
   target_lang: "en"
   source_lang: ["zh-CN", "ja", "ko"]
   backup: true

   # File processing
   include:
     - "**/*.py"
     - "**/*.js"
     - "**/*.md"

   exclude:
     - "**/node_modules/**"
     - "**/test_*"

Then simply run:

.. code-block:: bash

   langlint fix src/

Next Steps
----------

* Read the :doc:`usage` guide for detailed documentation
* Check the :doc:`configuration` for advanced options
* See the :doc:`cli` reference for all available commands

