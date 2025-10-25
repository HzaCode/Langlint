"""
Python parser for extracting translatable text from Python files.

This parser uses Python's built-in tokenize module to precisely extract
comments and docstrings while preserving the exact structure of the code.
"""

import tokenize
import io
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .base import Parser, TranslatableUnit, ParseResult, UnitType, ParseError


@dataclass
class PythonToken:
    """Represents a Python token with position information."""
    type: int
    string: str
    start: tuple[int, int]  # (line, column)
    end: tuple[int, int]
    line: str


class PythonParser(Parser):
    """
    Parser for Python files that extracts comments and docstrings.

    This parser uses Python's tokenize module to precisely identify
    and extract translatable text while maintaining exact positioning
    information for reconstruction.
    """

    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions."""
        return ['.py', '.pyi', '.pyw']

    @property
    def supported_mime_types(self) -> List[str]:
        """Return supported MIME types."""
        return [
            'text/x-python',
            'application/x-python-code',
            'text/x-python-script'
        ]

    def can_parse(self, file_path: str, content: Optional[str] = None) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file
            content: Optional file content

        Returns:
            True if this parser can handle the file
        """
        if content is None:
            return file_path.endswith(tuple(self.supported_extensions))

        # Simple heuristic: check for Python-specific patterns
        sample = content[:500].strip()

        # Must have Python-specific patterns
        python_patterns = [
            'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ',
            'return ', 'yield ', 'async ', 'await ', 'try:', 'except:',
            'finally:', 'with ', 'lambda ', 'and ', 'or ', 'not ',
            'in ', 'is ', '==', '!=', '<=', '>=', '=', '+=', '-=',
            '**', '//', '%', '&', '|', '^', '~', '<<', '>>'
        ]

        has_python_patterns = any(pattern in sample for pattern in python_patterns)

        # Additional check: if it's just plain text, reject
        if not has_python_patterns:
            # Check if it looks like plain text (no Python syntax)
            lines = [line.strip() for line in sample.split('\n') if line.strip()]
            if len(lines) > 1:
                # If multiple lines but no Python syntax, likely not Python
                return False

        return has_python_patterns

    def extract_translatable_units(self, content: str, file_path: str) -> ParseResult:
        """
        Extract translatable units from Python file content.

        Args:
            content: The file content to parse
            file_path: Path to the file

        Returns:
            ParseResult containing all translatable units found

        Raises:
            ParseError: If the file cannot be parsed
        """
        try:
            # Tokenize the content
            tokens = self._tokenize_content(content)

            # Extract translatable units
            units = []
            line_count = content.count('\n') + 1

            for token in tokens:
                unit = self._create_translatable_unit(token, content)
                if unit:
                    units.append(unit)

            return ParseResult(
                units=units,
                file_type="python",
                encoding="utf-8",
                line_count=line_count,
                metadata={
                    "parser": "PythonParser",
                    "version": "1.0.0"
                }
            )

        except Exception as e:
            raise ParseError(f"Failed to parse Python file {file_path}: {e}") from e

    def reconstruct_file(
        self,
        original_content: str,
        translated_units: List[TranslatableUnit],
        file_path: str
    ) -> str:
        """
        Reconstruct the file content with translated units.

        Args:
            original_content: The original file content
            translated_units: List of translated units
            file_path: Path to the file

        Returns:
            The reconstructed file content with translations applied
        """
        # Create a mapping of original content to translated content
        translation_map = {}
        for unit in translated_units:
            if unit.metadata and 'original_content' in unit.metadata:
                original = unit.metadata['original_content']
                # Store the unit itself to preserve metadata
                translation_map[original] = unit

        # Tokenize the original content
        tokens = self._tokenize_content(original_content)

        # Reconstruct the file
        lines = original_content.splitlines(keepends=True)

        # Process tokens in reverse order to avoid line number issues
        # when deleting lines for multi-line tokens
        for token in reversed(tokens):
            if token.type == tokenize.COMMENT:
                if token.string in translation_map:
                    unit = translation_map[token.string]
                    # For comments, rebuild with # prefix
                    new_token = f"# {unit.content}"
                    self._replace_token_in_lines(lines, token, new_token)
            elif token.type == tokenize.STRING:
                if token.string in translation_map:
                    unit = translation_map[token.string]
                    # For strings, preserve the original quote style
                    new_token = self._rebuild_string_token(token.string, unit.content)
                    self._replace_token_in_lines(lines, token, new_token)

        return ''.join(lines)

    def _tokenize_content(self, content: str) -> List[PythonToken]:
        """
        Tokenize Python content and return a list of tokens.

        Args:
            content: Python source code

        Returns:
            List of PythonToken objects
        """
        tokens = []

        try:
            for token_info in tokenize.generate_tokens(io.StringIO(content).readline):
                token = PythonToken(
                    type=token_info.type,
                    string=token_info.string,
                    start=token_info.start,
                    end=token_info.end,
                    line=token_info.line
                )
                tokens.append(token)
        except tokenize.TokenError as e:
            raise ParseError(f"Tokenization error: {e}") from e

        return tokens

    def _create_translatable_unit(self, token: PythonToken, content: str) -> Optional[TranslatableUnit]:
        """
        Create a translatable unit from a Python token.

        Args:
            token: Python token
            content: Original file content

        Returns:
            TranslatableUnit if the token is translatable, None otherwise
        """
        if token.type == tokenize.COMMENT:
            # Single-line comment
            comment_text = token.string[1:].strip()  # Remove # and whitespace
            if comment_text and self._is_translatable_text(comment_text):
                return TranslatableUnit(
                    content=comment_text,
                    unit_type=UnitType.COMMENT,
                    line_number=token.start[0],
                    column_number=token.start[1] + 1,  # Convert from 0-based to 1-based
                    context=f"Comment in {token.line.strip()}",
                    metadata={
                        'original_content': token.string,
                        'token_type': 'comment'
                    }
                )

        elif token.type == tokenize.STRING:
            # String literal (including docstrings)
            string_text = self._extract_string_content(token.string)
            if string_text and self._is_translatable_text(string_text):
                # Determine if it's a docstring or regular string
                unit_type = UnitType.DOCSTRING if self._is_docstring(token, content) else UnitType.STRING_LITERAL

                return TranslatableUnit(
                    content=string_text,
                    unit_type=unit_type,
                    line_number=token.start[0],
                    column_number=token.start[1] + 1,  # Convert from 0-based to 1-based
                    context=f"String literal: {token.line.strip()[:50]}...",
                    metadata={
                        'original_content': token.string,
                        'token_type': 'string',
                        'is_docstring': unit_type == UnitType.DOCSTRING
                    }
                )

        return None

    def _extract_string_content(self, string_token: str) -> str:
        """
        Extract the actual content from a string token.

        Args:
            string_token: The string token (including quotes)

        Returns:
            The string content without quotes
        """
        # Remove quotes and handle escape sequences
        # Handle f-strings, r-strings, b-strings, etc.
        prefix = ""
        token = string_token

        # Check for string prefixes (f, r, b, u, fr, rf, br, rb, etc.)
        while token and token[0].lower() in 'frbufrburfbr':
            prefix += token[0]
            token = token[1:]

        if token.startswith('"""') or token.startswith("'''"):
            # Multi-line string
            return token[3:-3]
        elif token.startswith('"') or token.startswith("'"):
            # Single-line string
            return token[1:-1]
        else:
            return string_token

    def _is_docstring(self, token: PythonToken, content: str) -> bool:
        """
        Check if a string token is a docstring.

        Args:
            token: String token to check
            content: Original file content

        Returns:
            True if the token is a docstring
        """
        # Check if it's at the module level or at the beginning of a function/class
        lines = content.splitlines()
        line_num = token.start[0] - 1

        if line_num >= len(lines):
            return False

        line = lines[line_num]

        # Check for docstring patterns
        if '"""' in line or "'''" in line:
            # Check if it's at the start of a function, class, or module
            stripped_line = line.strip()
            if stripped_line.startswith(('"""', "'''")):
                return True

            # Check if it's the first statement in a function/class
            # This is a simplified check - a full implementation would need AST parsing
            return True

        return False

    def _is_translatable_text(self, text: str) -> bool:
        """
        Check if text should be translated.

        Args:
            text: Text to check

        Returns:
            True if the text should be translated
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return False

        # Skip very short text (likely not meaningful)
        if len(text.strip()) < 3:
            return False

        # Skip text that's mostly punctuation or symbols
        if len([c for c in text if c.isalnum()]) < len(text) * 0.3:
            return False

        # Skip shebang lines
        if text.strip().startswith('#!'):
            return False

        # Skip shebang content (without the #)
        if text.strip().startswith('!/'):
            return False

        # Skip single character comments
        if len(text.strip()) <= 1:
            return False

        # Skip text that's mostly code or technical terms
        if self._is_mostly_code(text):
            return False

        # Skip Python special identifiers
        if self._is_python_special_identifier(text):
            return False

        # Skip technical strings (single words, short phrases)
        if self._is_technical_string(text):
            return False

        # Skip URLs and email addresses
        if self._is_url_or_email(text):
            return False

        # Only translate text containing non-English (non-ASCII) characters
        if not self._contains_non_english(text):
            return False

        return True

    def _is_mostly_code(self, text: str) -> bool:
        """
        Check if text is mostly code rather than natural language.

        Args:
            text: Text to check

        Returns:
            True if the text appears to be mostly code
        """
        # Check for strong code indicators (more specific patterns)
        strong_code_patterns = [
            'import ', 'from ', 'def ', 'class ', 'return ', 'yield ',
            'try:', 'except:', 'finally:', 'raise ', 'assert ',
            '==', '!=', '<=', '>=', '->', '=>', '+=', '-=', '*=', '/=',
            '()', '[]', '{}', '\\n', '\\t', '\\r',
        ]

        # Check for weaker code indicators (could also be natural language)
        weak_code_patterns = [
            '=', '(', ')', '[', ']', '{', '}', ':', ';', '\\'
        ]

        text_lower = text.lower()
        strong_count = sum(1 for pattern in strong_code_patterns if pattern in text_lower)
        weak_count = sum(1 for pattern in weak_code_patterns if pattern in text_lower)

        word_count = len(text.split())

        # If there are strong code indicators, it's likely code
        if strong_count >= 2:
            return True

        # If there are many weak indicators relative to word count, it's likely code
        if weak_count > word_count * 0.5:
            return True

        return False

    def _is_python_special_identifier(self, text: str) -> bool:
        """
        Check if text is a Python special identifier that shouldn't be translated.

        Args:
            text: Text to check

        Returns:
            True if the text is a Python special identifier
        """
        # Python special identifiers and keywords
        special_identifiers = {
            '__main__', '__init__', '__str__', '__repr__', '__len__', '__iter__',
            '__next__', '__enter__', '__exit__', '__call__', '__getitem__',
            '__setitem__', '__delitem__', '__contains__', '__bool__', '__int__',
            '__float__', '__complex__', '__round__', '__trunc__', '__floor__',
            '__ceil__', '__abs__', '__pos__', '__neg__', '__invert__', '__add__',
            '__sub__', '__mul__', '__truediv__', '__floordiv__', '__mod__',
            '__divmod__', '__pow__', '__lshift__', '__rshift__', '__and__',
            '__or__', '__xor__', '__lt__', '__le__', '__eq__', '__ne__',
            '__gt__', '__ge__', '__hash__', '__getattr__', '__setattr__',
            '__delattr__', '__dir__', '__getattribute__', '__setattribute__',
            '__delattribute__', '__new__', '__init_subclass__', '__class_getitem__',
            '__class__', '__bases__', '__name__', '__qualname__', '__module__',
            '__doc__', '__annotations__', '__dict__', '__weakref__', '__slots__',
            '__mro__', '__mro_entries__', '__subclasscheck__', '__subclasshook__',
            '__instancecheck__', '__abstractmethods__', '__isabstractmethod__',
            '__wrapped__', '__wrapped__', '__self__', '__func__', '__self__',
            '__func__', '__self__', '__func__', '__self__', '__func__',
            'self', 'cls', 'args', 'kwargs', 'True', 'False', 'None',
            'Ellipsis', 'NotImplemented', 'Exception', 'BaseException',
            'object', 'type', 'property', 'staticmethod', 'classmethod',
            'super', 'isinstance', 'issubclass', 'hasattr', 'getattr',
            'setattr', 'delattr', 'dir', 'vars', 'locals', 'globals',
            'compile', 'eval', 'exec', 'open', 'print', 'input', 'len',
            'min', 'max', 'sum', 'all', 'any', 'enumerate', 'range',
            'zip', 'map', 'filter', 'sorted', 'reversed', 'iter', 'next',
            'bin', 'oct', 'hex', 'chr', 'ord', 'ascii', 'repr', 'str',
            'int', 'float', 'complex', 'bool', 'list', 'tuple', 'dict',
            'set', 'frozenset', 'bytes', 'bytearray', 'memoryview',
            'slice', 'range', 'enumerate', 'zip', 'map', 'filter',
            'reversed', 'sorted', 'any', 'all', 'sum', 'min', 'max',
            'abs', 'round', 'divmod', 'pow', 'hash', 'id', 'type',
            'isinstance', 'issubclass', 'callable', 'getattr', 'setattr',
            'delattr', 'hasattr', 'dir', 'vars', 'locals', 'globals',
            'compile', 'eval', 'exec', 'open', 'print', 'input', 'len',
            'min', 'max', 'sum', 'all', 'any', 'enumerate', 'range',
            'zip', 'map', 'filter', 'sorted', 'reversed', 'iter', 'next'
        }

        return text.strip() in special_identifiers

    def _is_technical_string(self, text: str) -> bool:
        """
        Check if text is a technical string that shouldn't be translated.

        Args:
            text: Text to check

        Returns:
            True if the text is a technical string
        """
        text = text.strip()

        # Skip single words that are likely technical terms
        if len(text.split()) == 1:
            # Common technical single words
            technical_words = {
                'hello', 'world', 'test', 'demo', 'example', 'sample',
                'data', 'info', 'config', 'settings', 'options', 'params',
                'args', 'kwargs', 'result', 'output', 'input', 'value',
                'key', 'id', 'name', 'type', 'class', 'method', 'function',
                'variable', 'constant', 'enum', 'flag', 'status', 'state',
                'mode', 'level', 'version', 'build', 'release', 'debug',
                'error', 'warning', 'info', 'log', 'trace', 'stack',
                'exception', 'error', 'warning', 'info', 'debug', 'trace',
                'verbose', 'quiet', 'silent', 'normal', 'fast', 'slow',
                'high', 'low', 'medium', 'small', 'large', 'big', 'tiny',
                'min', 'max', 'avg', 'sum', 'count', 'total', 'size',
                'length', 'width', 'height', 'depth', 'weight', 'speed',
                'time', 'date', 'year', 'month', 'day', 'hour', 'minute',
                'second', 'millisecond', 'microsecond', 'nanosecond',
                'true', 'false', 'yes', 'no', 'on', 'off', 'enabled',
                'disabled', 'active', 'inactive', 'running', 'stopped',
                'paused', 'resumed', 'started', 'finished', 'completed',
                'failed', 'success', 'ok', 'okay', 'good', 'bad', 'great',
                'awesome', 'cool', 'nice', 'perfect', 'excellent', 'wonderful',
                'amazing', 'incredible', 'fantastic', 'terrible', 'awful',
                'horrible', 'disgusting', 'ugly', 'beautiful', 'pretty',
                'cute', 'lovely', 'sweet', 'kind', 'nice', 'good', 'bad',
                'evil', 'wrong', 'right', 'correct', 'incorrect', 'valid',
                'invalid', 'legal', 'illegal', 'allowed', 'forbidden',
                'permitted', 'denied', 'granted', 'refused', 'accepted',
                'rejected', 'approved', 'disapproved', 'confirmed', 'denied',
                # Common dictionary keys and technical identifiers
                'username', 'password', 'email', 'user_type', 'created_at',
                'last_login', 'is_active', 'login_time', 'permissions',
                'session_id', 'admin', 'user', 'guest', 'read', 'write',
                'delete', 'manage_users', 'admin123', 'user123', 'guest123'
            }
            return text.lower() in technical_words

        # Skip common technical phrases
        if len(text.split()) <= 3:
            technical_phrases = {
                'hello world', 'hello, world', 'hello, world!', 'hello world!',
                'test case', 'demo app', 'example code', 'sample data',
                'config file', 'settings file', 'options menu', 'input field',
                'output field', 'result set', 'data table', 'error message',
                'warning message', 'info message', 'debug info', 'log file',
                'trace file', 'stack trace', 'exception handler', 'error handler',
                'warning handler', 'info handler', 'debug handler', 'verbose mode',
                'quiet mode', 'silent mode', 'normal mode', 'fast mode',
                'slow mode', 'high level', 'low level', 'medium level',
                'small size', 'large size', 'big size', 'tiny size',
                'min value', 'max value', 'avg value', 'sum value',
                'count value', 'total value', 'size value', 'length value',
                'width value', 'height value', 'depth value', 'weight value',
                'speed value', 'time value', 'date value', 'year value',
                'month value', 'day value', 'hour value', 'minute value',
                'second value', 'millisecond value', 'microsecond value',
                'nanosecond value', 'true value', 'false value', 'yes value',
                'no value', 'on value', 'off value', 'enabled value',
                'disabled value', 'active value', 'inactive value', 'running value',
                'stopped value', 'paused value', 'resumed value', 'started value',
                'finished value', 'completed value', 'failed value', 'success value',
                'ok value', 'okay value', 'good value', 'bad value', 'great value',
                'awesome value', 'cool value', 'nice value', 'perfect value',
                'excellent value', 'wonderful value', 'amazing value', 'incredible value',
                'fantastic value', 'terrible value', 'awful value', 'horrible value',
                'disgusting value', 'ugly value', 'beautiful value', 'pretty value',
                'cute value', 'lovely value', 'sweet value', 'kind value', 'nice value',
                'good value', 'bad value', 'evil value', 'wrong value', 'right value',
                'correct value', 'incorrect value', 'valid value', 'invalid value',
                'legal value', 'illegal value', 'allowed value', 'forbidden value',
                'permitted value', 'denied value', 'granted value', 'refused value',
                'accepted value', 'rejected value', 'approved value', 'disapproved value',
                'confirmed value', 'denied value'
            }
            return text.lower() in technical_phrases

        # Skip very short phrases
        if len(text) < 10:
            return True

        # Skip phrases that are mostly technical
        technical_phrases = [
            'hello world', 'test case', 'demo app', 'example code',
            'sample data', 'config file', 'settings file', 'options menu',
            'input field', 'output field', 'result set', 'data table',
            'error message', 'warning message', 'info message', 'debug info',
            'log file', 'trace file', 'stack trace', 'exception handler',
            'error handler', 'warning handler', 'info handler', 'debug handler',
            'verbose mode', 'quiet mode', 'silent mode', 'normal mode',
            'fast mode', 'slow mode', 'high level', 'low level', 'medium level',
            'small size', 'large size', 'big size', 'tiny size', 'min value',
            'max value', 'avg value', 'sum value', 'count value', 'total value',
            'size value', 'length value', 'width value', 'height value',
            'depth value', 'weight value', 'speed value', 'time value',
            'date value', 'year value', 'month value', 'day value',
            'hour value', 'minute value', 'second value', 'millisecond value',
            'microsecond value', 'nanosecond value', 'true value', 'false value',
            'yes value', 'no value', 'on value', 'off value', 'enabled value',
            'disabled value', 'active value', 'inactive value', 'running value',
            'stopped value', 'paused value', 'resumed value', 'started value',
            'finished value', 'completed value', 'failed value', 'success value',
            'ok value', 'okay value', 'good value', 'bad value', 'great value',
            'awesome value', 'cool value', 'nice value', 'perfect value',
            'excellent value', 'wonderful value', 'amazing value', 'incredible value',
            'fantastic value', 'terrible value', 'awful value', 'horrible value',
            'disgusting value', 'ugly value', 'beautiful value', 'pretty value',
            'cute value', 'lovely value', 'sweet value', 'kind value', 'nice value',
            'good value', 'bad value', 'evil value', 'wrong value', 'right value',
            'correct value', 'incorrect value', 'valid value', 'invalid value',
            'legal value', 'illegal value', 'allowed value', 'forbidden value',
            'permitted value', 'denied value', 'granted value', 'refused value',
            'accepted value', 'rejected value', 'approved value', 'disapproved value',
            'confirmed value', 'denied value'
        ]

        return text.lower() in technical_phrases

    def _is_url_or_email(self, text: str) -> bool:
        """
        Check if text is a URL or email address.

        Args:
            text: Text to check

        Returns:
            True if the text is a URL or email address
        """
        import re

        # URL pattern
        url_pattern = r'^https?://|^ftp://|^file://|^www\.'
        # Email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        return bool(re.match(url_pattern, text.strip()) or re.match(email_pattern, text.strip()))

    def _contains_non_english(self, text: str) -> bool:
        """
        Check if text contains non-English (non-ASCII) characters.

        Args:
            text: Text to check

        Returns:
            True if the text contains non-ASCII characters
        """
        # Check if any character is outside the ASCII range (0-127)
        return any(ord(char) > 127 for char in text)

    def _rebuild_string_token(self, original_token: str, translated_content: str) -> str:
        """
        Rebuild a string token with translated content while preserving quote style.

        Args:
            original_token: The original string token (including quotes)
            translated_content: The translated content (without quotes)

        Returns:
            The rebuilt string token with the same quote style
        """
        # Extract prefix (f, r, b, etc.)
        prefix = ""
        token = original_token
        while token and token[0].lower() in 'frbufrburfbr':
            prefix += token[0]
            token = token[1:]

        # Detect the quote style
        if token.startswith('"""'):
            return f'{prefix}"""{translated_content}"""'
        elif token.startswith("'''"):
            return f"{prefix}'''{translated_content}'''"
        elif token.startswith('"'):
            return f'{prefix}"{translated_content}"'
        elif token.startswith("'"):
            return f"{prefix}'{translated_content}'"
        else:
            # Fallback: use double quotes
            return f'{prefix}"{translated_content}"'

    def _replace_token_in_lines(self, lines: List[str], token: PythonToken, new_content: str) -> None:
        """
        Replace a token in the lines list with new content.

        Args:
            lines: List of lines (modified in place)
            token: Token to replace
            new_content: New content to replace with
        """
        # Handle multi-line tokens (like multi-line docstrings)
        start_line = token.start[0] - 1  # Convert to 0-based index
        end_line = token.end[0] - 1

        if start_line >= len(lines) or start_line < 0:
            return

        if start_line == end_line:
            # Single-line token
            line = lines[start_line]
            start_col = token.start[1]
            end_col = token.end[1]

            # Replace the token in the line
            new_line = line[:start_col] + new_content + line[end_col:]
            lines[start_line] = new_line
        else:
            # Multi-line token (e.g., multi-line docstring)
            start_col = token.start[1]
            end_col = token.end[1]

            # Get content before token on start line
            before_token = lines[start_line][:start_col]

            # Get content after token on end line (if end line exists)
            after_token = ""
            if end_line < len(lines):
                after_token = lines[end_line][end_col:]

            # Replace: keep before, insert new content, keep after
            new_line = before_token + new_content + after_token
            lines[start_line] = new_line

            # Remove the middle and end lines
            for i in range(end_line, start_line, -1):
                if i < len(lines):
                    del lines[i]
