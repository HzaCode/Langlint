# Contributing Guide

Thank you for your interest in the LangLint project! We welcome contributions of all kinds, including code, documentation, tests, examples, issue reports, and more.

## Ways to Contribute

### 1. Report Issues

If you find a bug or have a feature suggestion, please:

1. Check [existing Issues](https://github.com/HzaCode/Langlint/issues) to confirm the issue hasn't been reported
2. Use the [Issue template](https://github.com/HzaCode/Langlint/issues/new/choose) to create a new issue
3. Provide detailed problem description, reproduction steps, and expected behavior

### 2. Submit Code

#### Development Workflow

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/langlint.git
   cd langlint
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   
   pip install -e ".[dev]"
   pre-commit install
   ```

4. **Development**
   - Write code
   - Add tests
   - Update documentation

5. **Run tests**
   ```bash
   pytest
   black --check langlint/
   ruff check langlint/
   mypy langlint/
   bandit -r langlint/
   ```

6. **Commit changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

7. **Create Pull Request**
   - Use the [PR template](https://github.com/HzaCode/Langlint/compare)
   - Describe changes in detail
   - Link related issues

#### Code Standards

- **Code formatting**: Use Black
- **Code checking**: Use Ruff
- **Type checking**: Use MyPy
- **Security checking**: Use Bandit
- **Commit messages**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

#### Testing Requirements

- **Unit tests**: New features must include unit tests
- **Integration tests**: Complex features need integration tests
- **Test coverage**: Maintain ≥ 85% coverage
- **Documentation tests**: Update relevant documentation

### 3. Documentation Contributions

#### Documentation Types

- **API documentation**: Docstrings for functions and classes
- **User guides**: Usage tutorials and examples
- **Developer documentation**: Architecture design and development guides
- **Translations**: Multi-language documentation support

#### Documentation Standards

- **Format**: Use Markdown format
- **Structure**: Follow existing documentation structure
- **Language**: Use clear and concise English
- **Examples**: Provide runnable code examples

### 4. Example Contributions

#### Example Types

- **Usage examples**: Demonstrate basic usage
- **Advanced examples**: Demonstrate complex scenarios
- **Integration examples**: Integration with other tools
- **Best practices**: Recommended usage patterns

#### Example Requirements

- **Runnable**: Ensure examples can run properly
- **Documented**: Provide detailed explanations
- **Tested**: Include automated tests
- **Updated**: Keep synchronized with latest versions

## Development Guide

### Project Structure

```
langlint/
├── langlint/                 # Core package
│   ├── core/                # Core components
│   ├── parsers/             # Parsers
│   ├── translators/         # Translators
│   └── cli.py              # Command line interface
├── tests/                   # Tests
├── docs/                    # Documentation
├── examples/                # Examples
├── scripts/                 # Scripts
└── .github/                 # GitHub configuration
```

### Development Environment Setup

#### 1. Clone the repository

```bash
git clone https://github.com/HzaCode/Langlint.git
cd langlint
```

#### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

#### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

#### 4. Install pre-commit hooks

```bash
pre-commit install
```

#### 5. Run tests

```bash
pytest
```

### Code Quality Tools

#### Black (Code Formatting)

```bash
# Format code
black langlint/

# Check formatting
black --check langlint/
```

#### Ruff (Code Checking)

```bash
# Check code
ruff check langlint/

# Auto-fix
ruff check --fix langlint/
```

#### MyPy (Type Checking)

```bash
# Type checking
mypy langlint/
```

#### Bandit (Security Checking)

```bash
# Security checking
bandit -r langlint/
```

### Testing Guide

#### Running Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_python_parser.py

# Run integration tests
pytest tests/integration/

# Generate coverage report
pytest --cov=langlint --cov-report=html
```

#### Writing Tests

```python
def test_example():
    """Test example"""
    # Prepare test data
    input_data = "test input"
    
    # Execute test
    result = function_under_test(input_data)
    
    # Verify results
    assert result == "expected output"
```

### Documentation Guide

#### Docstrings

```python
def example_function(param1: str, param2: int) -> str:
    """
    Example function docstring
    
    Args:
        param1: First parameter
        param2: Second parameter
    
    Returns:
        Return result
    
    Raises:
        ValueError: When parameter is invalid
    
    Example:
        >>> example_function("hello", 42)
        "hello42"
    """
    pass
```

#### Markdown Documentation

```markdown
# Title

## Subtitle

### Code Example

```python
# Code example
def hello():
    return "Hello, World!"
```

### Lists

- Item 1
- Item 2
- Item 3
```

## Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/) control:

- **Major version**: Incompatible API changes
- **Minor version**: Backward compatible feature additions
- **Patch version**: Backward compatible bug fixes

### Release Steps

1. **Update version number**
   ```bash
   # Update version number in pyproject.toml
   # Update CHANGELOG.md
   ```

2. **Create release tag**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Automatic release**
   - GitHub Actions will automatically build and release to PyPI
   - Create GitHub Release

## Community Participation

### Discussions

- **GitHub Discussions**: Feature discussions and Q&A
- **GitHub Issues**: Bug reports and feature requests
- **Mailing list**: Important announcements and discussions

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Getting Help

If you need help:

1. Check the [documentation](https://github.com/HzaCode/Langlint)
2. Search [existing issues](https://github.com/HzaCode/Langlint/issues)
3. Ask in [Discussions](https://github.com/HzaCode/Langlint/discussions)
4. Send email to ang@hezhiang.com

## Contributors

Thank you to all developers and users who have contributed to LangLint!

### How to Become a Contributor

1. Submit your first Pull Request
2. Participate in community discussions
3. Help other users
4. Improve documentation and examples

### Contributor Benefits

- Listed in README contributors
- Earn contributor badges
- Participate in project decisions
- Get priority technical support

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Thank you for contributing to the LangLint project!* 🚀