"""
Generic code parser for extracting comments from various programming languages.

This parser uses pre-compiled, high-performance regular expressions to identify
single-line and block comments in various programming languages.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .base import Parser, TranslatableUnit, ParseResult, UnitType, ParseError


@dataclass
class CommentPattern:
    """Represents a comment pattern for a programming language."""
    single_line: List[str]
    block_start: Optional[str] = None
    block_end: Optional[str] = None
    block_nested: bool = False


class GenericCodeParser(Parser):
    """
    Generic parser for various programming languages that extracts comments.

    This parser uses pre-compiled regular expressions to identify and extract
    single-line and block comments from various programming languages.
    """

    # Language-specific comment patterns
    COMMENT_PATTERNS = {
        '.js': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.ts': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.go': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.rs': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.java': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.cpp': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.c': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.h': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.cs': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.php': CommentPattern(
            single_line=['//', '#'],
            block_start='/*',
            block_end='*/'
        ),
        '.rb': CommentPattern(
            single_line=['#'],
            block_start='=begin',
            block_end='=end'
        ),
        '.sh': CommentPattern(
            single_line=['#']
        ),
        '.bash': CommentPattern(
            single_line=['#']
        ),
        '.zsh': CommentPattern(
            single_line=['#']
        ),
        '.fish': CommentPattern(
            single_line=['#']
        ),
        '.sql': CommentPattern(
            single_line=['--'],
            block_start='/*',
            block_end='*/'
        ),
        '.r': CommentPattern(
            single_line=['#']
        ),
        '.m': CommentPattern(
            single_line=['%'],
            block_start='%{',
            block_end='%}'
        ),
        '.scala': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.kt': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.swift': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.dart': CommentPattern(
            single_line=['//'],
            block_start='/*',
            block_end='*/'
        ),
        '.lua': CommentPattern(
            single_line=['--'],
            block_start='--[[',
            block_end=']]'
        ),
        '.vim': CommentPattern(
            single_line=['"']
        ),
        '.yaml': CommentPattern(
            single_line=['#']
        ),
        '.yml': CommentPattern(
            single_line=['#']
        ),
        '.toml': CommentPattern(
            single_line=['#']
        ),
        '.ini': CommentPattern(
            single_line=[';', '#']
        ),
        '.cfg': CommentPattern(
            single_line=[';', '#']
        ),
        '.conf': CommentPattern(
            single_line=['#']
        ),
        '.dockerfile': CommentPattern(
            single_line=['#']
        ),
        '.makefile': CommentPattern(
            single_line=['#']
        ),
        '.cmake': CommentPattern(
            single_line=['#']
        ),
    }

    def __init__(self):
        """Initialize the generic code parser."""
        # Pre-compile regular expressions for better performance
        self._compiled_patterns = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regular expressions for all supported languages."""
        for ext, pattern in self.COMMENT_PATTERNS.items():
            compiled = {}

            # Compile single-line comment patterns
            compiled['single_line'] = []
            for sl_pattern in pattern.single_line:
                # Escape special regex characters
                escaped = re.escape(sl_pattern)
                # Match the pattern followed by optional whitespace and content
                regex = rf'^\s*{escaped}\s*(.*)$'
                compiled['single_line'].append(re.compile(regex, re.MULTILINE))

            # Compile block comment patterns
            if pattern.block_start and pattern.block_end:
                start_escaped = re.escape(pattern.block_start)
                end_escaped = re.escape(pattern.block_end)

                # Pattern for block comments
                if pattern.block_nested:
                    # Handle nested comments (like C-style)
                    regex = rf'{start_escaped}(?:(?!{end_escaped}).)*{end_escaped}'
                else:
                    # Non-nested comments
                    regex = rf'{start_escaped}.*?{end_escaped}'

                compiled['block'] = re.compile(regex, re.DOTALL | re.MULTILINE)

            self._compiled_patterns[ext] = compiled

    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions."""
        return list(self.COMMENT_PATTERNS.keys())

    @property
    def supported_mime_types(self) -> List[str]:
        """Return supported MIME types."""
        return [
            'text/x-javascript',
            'text/x-typescript',
            'text/x-go',
            'text/x-rust',
            'text/x-java',
            'text/x-c++',
            'text/x-c',
            'text/x-csharp',
            'text/x-php',
            'text/x-ruby',
            'text/x-shellscript',
            'text/x-sql',
            'text/x-r',
            'text/x-matlab',
            'text/x-scala',
            'text/x-kotlin',
            'text/x-swift',
            'text/x-dart',
            'text/x-lua',
            'text/x-vim',
            'text/x-yaml',
            'text/x-toml',
            'text/x-ini',
            'text/x-dockerfile',
            'text/x-makefile',
            'text/x-cmake',
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

        # Check if content looks like code with comments
        if not content.strip():
            return False

        # Look for comment patterns in the content
        for ext, pattern in self.COMMENT_PATTERNS.items():
            if file_path.endswith(ext):
                # Check for single-line comments
                for sl_pattern in pattern.single_line:
                    if sl_pattern in content:
                        return True

                # Check for block comments
                if pattern.block_start and pattern.block_end:
                    if pattern.block_start in content and pattern.block_end in content:
                        return True

        return False

    def extract_translatable_units(self, content: str, file_path: str) -> ParseResult:
        """
        Extract translatable units from code file content.

        Args:
            content: The file content to parse
            file_path: Path to the file

        Returns:
            ParseResult containing all translatable units found

        Raises:
            ParseError: If the file cannot be parsed
        """
        try:
            # Determine file extension
            ext = self._get_file_extension(file_path)
            if ext not in self.COMMENT_PATTERNS:
                raise ParseError(f"Unsupported file extension: {ext}")

            # Get comment pattern for this file type
            pattern = self.COMMENT_PATTERNS[ext]
            compiled = self._compiled_patterns[ext]

            # Extract translatable units
            units = []

            # Extract single-line comments
            for regex in compiled['single_line']:
                for match in regex.finditer(content):
                    comment_text = match.group(1).strip()
                    if comment_text and self._is_translatable_text(comment_text):
                        line_num = content[:match.start()].count('\n') + 1
                        col_num = max(1, match.start() - content.rfind('\n', 0, match.start()))

                        units.append(TranslatableUnit(
                            content=comment_text,
                            unit_type=UnitType.COMMENT,
                            line_number=line_num,
                            column_number=col_num,
                            context=f"Comment in {ext} file",
                            metadata={
                                'original_content': match.group(0),
                                'file_extension': ext,
                                'comment_type': 'single_line'
                            }
                        ))

            # Extract block comments
            if 'block' in compiled:
                for match in compiled['block'].finditer(content):
                    comment_text = self._extract_block_comment_content(
                        match.group(0), pattern.block_start, pattern.block_end
                    )

                    if comment_text and self._is_translatable_text(comment_text):
                        line_num = content[:match.start()].count('\n') + 1
                        col_num = max(1, match.start() - content.rfind('\n', 0, match.start()))

                        units.append(TranslatableUnit(
                            content=comment_text,
                            unit_type=UnitType.COMMENT,
                            line_number=line_num,
                            column_number=col_num,
                            context=f"Block comment in {ext} file",
                            metadata={
                                'original_content': match.group(0),
                                'file_extension': ext,
                                'comment_type': 'block'
                            }
                        ))

            return ParseResult(
                units=units,
                file_type="generic_code",
                encoding="utf-8",
                line_count=content.count('\n') + 1,
                metadata={
                    "parser": "GenericCodeParser",
                    "version": "1.0.0",
                    "file_extension": ext,
                    "language": self._get_language_name(ext)
                }
            )

        except Exception as e:
            raise ParseError(f"Failed to parse code file {file_path}: {e}") from e

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
                translation_map[original] = unit.content

        # Replace comments in the content
        result = original_content
        for original, translated in translation_map.items():
            result = result.replace(original, translated)

        return result

    def _get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension from a file path.

        Args:
            file_path: Path to the file

        Returns:
            File extension (e.g., '.js')
        """
        return '.' + file_path.split('.')[-1].lower()

    def _extract_block_comment_content(
        self,
        comment: str,
        start_pattern: str,
        end_pattern: str
    ) -> str:
        """
        Extract the actual content from a block comment.

        Args:
            comment: The full block comment
            start_pattern: Start pattern (e.g., '/*')
            end_pattern: End pattern (e.g., '*/')

        Returns:
            The comment content without start/end patterns
        """
        # Remove start and end patterns
        content = comment
        if content.startswith(start_pattern):
            content = content[len(start_pattern):]
        if content.endswith(end_pattern):
            content = content[:-len(end_pattern)]

        # Clean up the content
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove leading asterisks and whitespace (common in block comments)
            cleaned_line = re.sub(r'^\s*\*+\s*', '', line)
            cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines).strip()

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

        # Skip very short text
        if len(text.strip()) < 3:
            return False

        # Skip text that's mostly code
        if self._is_mostly_code(text):
            return False

        # Skip text that's mostly punctuation or symbols
        if len([c for c in text if c.isalnum()]) < len(text) * 0.3:
            return False

        # Skip URLs and email addresses
        if re.match(r'^https?://|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text.strip()):
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
        # Check for common code patterns
        code_patterns = [
            r'import\s+',  # Import statements
            r'from\s+',    # From statements
            r'def\s+',     # Function definitions
            r'class\s+',   # Class definitions
            r'function\s+', # Function definitions
            r'var\s+',     # Variable declarations
            r'let\s+',     # Variable declarations
            r'const\s+',   # Constant declarations
            r'if\s*\(',    # If statements
            r'for\s*\(',   # For loops
            r'while\s*\(', # While loops
            r'return\s+',  # Return statements
            r'console\.',  # Console statements
            r'System\.',   # System statements
            r'printf\s*\(', # Print statements
            r'println\s*\(', # Print statements
            r'#include',   # Include statements
            r'using\s+',   # Using statements
            r'namespace\s+', # Namespace statements
            r'public\s+',  # Public declarations
            r'private\s+', # Private declarations
            r'protected\s+', # Protected declarations
            r'static\s+',  # Static declarations
            r'final\s+',   # Final declarations
            r'abstract\s+', # Abstract declarations
            r'interface\s+', # Interface declarations
            r'enum\s+',    # Enum declarations
            r'struct\s+',  # Struct declarations
            r'union\s+',   # Union declarations
            r'typedef\s+', # Typedef declarations
            r'#define',    # Define statements
            r'#ifdef',     # Ifdef statements
            r'#ifndef',    # Ifndef statements
            r'#endif',     # Endif statements
            r'#pragma',    # Pragma statements
            r'#warning',   # Warning statements
            r'#error',     # Error statements
        ]

        code_count = sum(1 for pattern in code_patterns if re.search(pattern, text, re.IGNORECASE))
        return code_count > len(text.split()) * 0.3

    def _get_language_name(self, ext: str) -> str:
        """
        Get the human-readable language name for a file extension.

        Args:
            ext: File extension

        Returns:
            Language name
        """
        language_names = {
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.sh': 'Shell Script',
            '.bash': 'Bash',
            '.zsh': 'Zsh',
            '.fish': 'Fish',
            '.sql': 'SQL',
            '.r': 'R',
            '.m': 'MATLAB',
            '.scala': 'Scala',
            '.kt': 'Kotlin',
            '.swift': 'Swift',
            '.dart': 'Dart',
            '.lua': 'Lua',
            '.vim': 'Vim Script',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.cfg': 'Configuration',
            '.conf': 'Configuration',
            '.dockerfile': 'Dockerfile',
            '.makefile': 'Makefile',
            '.cmake': 'CMake',
        }

        return language_names.get(ext, 'Unknown')

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
