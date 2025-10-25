Installation
============

Requirements
------------

* Python 3.8 or higher
* pip, pipx, or uv package manager

Installation Methods
--------------------

Using pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install langlint

Using pipx (Isolated Environment)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pipx install langlint

Using uv (Fastest)
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv tool install langlint

Verifying Installation
----------------------

After installation, verify that LangLint is installed correctly:

.. code-block:: bash

   langlint --version

You should see output similar to:

.. code-block:: text

   langlint, version 1.0.0

Development Installation
------------------------

For development, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/HzaCode/Langlint.git
   cd langlint
   pip install -e ".[dev]"

This will install LangLint along with all development dependencies including:

* pytest - for testing
* black - for code formatting
* ruff - for linting
* mypy - for type checking
* sphinx - for documentation

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   # For pip users
   pip install --upgrade langlint

   # For pipx users
   pipx upgrade langlint

   # For uv users
   uv tool upgrade langlint

Uninstallation
--------------

To uninstall LangLint:

.. code-block:: bash

   # For pip users
   pip uninstall langlint

   # For pipx users
   pipx uninstall langlint

   # For uv users
   uv tool uninstall langlint

