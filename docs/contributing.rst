Contributing
============

Thank you for your interest in contributing to LangLint! We welcome contributions of all kinds.

Ways to Contribute
------------------

* Report bugs and request features via GitHub Issues
* Submit pull requests to fix bugs or add features
* Improve documentation
* Write tutorials and examples
* Help answer questions in Discussions

Getting Started
---------------

1. Fork the Repository
~~~~~~~~~~~~~~~~~~~~~~

Fork the repository on GitHub and clone your fork:

.. code-block:: bash

   git clone https://github.com/YOUR_USERNAME/langlint.git
   cd langlint

2. Set Up Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install development dependencies
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install

3. Make Your Changes
~~~~~~~~~~~~~~~~~~~~

Create a new branch for your changes:

.. code-block:: bash

   git checkout -b feature/your-feature-name

Make your changes and ensure:

* Code follows the project style (Black, Ruff)
* All tests pass
* New features include tests
* Documentation is updated

4. Run Tests
~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=langlint --cov-report=term-missing

   # Run specific test
   pytest tests/test_cli.py

5. Code Quality Checks
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Format code
   black langlint/ tests/

   # Lint code
   ruff check langlint/ tests/

   # Type check
   mypy langlint/

   # Security check
   bandit -r langlint/

6. Submit Pull Request
~~~~~~~~~~~~~~~~~~~~~~

Push your changes and create a pull request:

.. code-block:: bash

   git push origin feature/your-feature-name

Then open a pull request on GitHub with:

* Clear description of changes
* Reference to related issues
* Test results

Development Guidelines
----------------------

Code Style
~~~~~~~~~~

* Follow PEP 8
* Use Black for formatting (line length: 100)
* Use type hints
* Write docstrings for all public APIs

Testing
~~~~~~~

* Write tests for all new features
* Maintain test coverage ≥ 85%
* Use pytest fixtures for common setup
* Test edge cases and error handling

Documentation
~~~~~~~~~~~~~

* Update docstrings for code changes
* Update RST files for user-facing changes
* Add examples for new features
* Keep documentation in sync with code

Commit Messages
~~~~~~~~~~~~~~~

Follow Conventional Commits:

.. code-block:: text

   feat: add support for new file type
   fix: correct translation of multiline strings
   docs: update installation guide
   test: add tests for edge cases
   chore: update dependencies

Project Structure
-----------------

.. code-block:: text

   langlint/
   ├── langlint/           # Python package
   │   ├── core/          # Core functionality
   │   ├── parsers/       # File parsers
   │   ├── translators/   # Translation services
   │   └── cli.py         # CLI interface
   ├── crates/            # Rust implementation
   ├── tests/             # Test suite
   ├── docs/              # Documentation
   └── examples/          # Usage examples

Adding a New Parser
-------------------

To add support for a new file type:

1. Create ``langlint/parsers/your_parser.py``
2. Inherit from ``Parser`` abstract class
3. Implement required methods:
   * ``supported_extensions``
   * ``supported_mime_types``
   * ``can_parse()``
   * ``extract_translatable_units()``
   * ``reconstruct_file()``
4. Add tests in ``tests/test_your_parser.py``
5. Update documentation

Example:

.. code-block:: python

   from langlint.parsers.base import Parser, ParseResult

   class YourParser(Parser):
       @property
       def supported_extensions(self):
           return ['.ext']

       def can_parse(self, file_path, content=None):
           return file_path.endswith('.ext')

       def extract_translatable_units(self, content, file_path):
           # Parse and extract units
           pass

       def reconstruct_file(self, original, translated, file_path):
           # Reconstruct file with translations
           pass

Adding a Translator
-------------------

To add a new translation service:

1. Create ``langlint/translators/your_translator.py``
2. Inherit from ``Translator`` abstract class
3. Implement required methods
4. Add configuration handling
5. Add tests
6. Update documentation

Code of Conduct
---------------

Please read and follow our :doc:`Code of Conduct <../CODE_OF_CONDUCT>`.

Getting Help
------------

If you need help:

* Check the documentation
* Search existing issues
* Ask in GitHub Discussions
* Email: ang@hezhiang.com

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.

