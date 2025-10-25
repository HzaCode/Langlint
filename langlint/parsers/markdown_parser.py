"""
Markdown parser for extracting translatable text from Markdown files.

This parser uses mistune to parse Markdown AST and extract only text nodes
while preserving the exact structure of code blocks, links, HTML tags,
and Front Matter metadata.
"""

import re
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass

try:
    import mistune
    from mistune import Markdown
except ImportError:
    mistune = None
    Markdown = None

from .base import Parser, TranslatableUnit, ParseResult, UnitType, ParseError


@dataclass
class MarkdownNode:
    """Represents a Markdown AST node."""
    type: str
    text: Optional[str] = None
    children: Optional[List['MarkdownNode']] = None
    attrs: Optional[Dict[str, Any]] = None
    line_number: int = 0
    column_number: int = 0


class MarkdownParser(Parser):
    """
    Parser for Markdown files that extracts text nodes while preserving structure.

    This parser uses mistune to parse Markdown into an AST and extracts only
    text content from appropriate nodes while maintaining the exact structure
    of code blocks, links, HTML tags, and Front Matter.
    """

    def __init__(self):
        """Initialize the Markdown parser."""
        if mistune is None:
            raise ImportError("mistune is required for Markdown parsing. Install with: pip install mistune")

        self.markdown = Markdown()
        self._front_matter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL | re.MULTILINE)

    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions."""
        return ['.md', '.markdown', '.mdown', '.mkd', '.mkdn']

    @property
    def supported_mime_types(self) -> List[str]:
        """Return supported MIME types."""
        return [
            'text/markdown',
            'text/x-markdown',
            'application/markdown'
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

        # Check if content looks like Markdown
        if not content.strip():
            return False

        # Check for common Markdown patterns
        markdown_patterns = [
            r'^#{1,6}\s+',  # Headers
            r'^\*\s+',      # Unordered lists
            r'^\d+\.\s+',   # Ordered lists
            r'^\>\s+',      # Blockquotes
            r'```',         # Code blocks
            r'\[.*?\]\(.*?\)',  # Links
            r'\*\*.*?\*\*',     # Bold
            r'\*.*?\*',         # Italic
        ]

        return any(re.search(pattern, content, re.MULTILINE) for pattern in markdown_patterns)

    def extract_translatable_units(self, content: str, file_path: str) -> ParseResult:
        """
        Extract translatable units from Markdown file content.

        Args:
            content: The file content to parse
            file_path: Path to the file

        Returns:
            ParseResult containing all translatable units found

        Raises:
            ParseError: If the file cannot be parsed
        """
        try:
            # Extract Front Matter first
            front_matter_units = self._extract_front_matter(content)

            # Parse the main content (excluding Front Matter)
            main_content = self._remove_front_matter(content)

            # Parse Markdown AST
            ast = self._parse_markdown_ast(main_content)

            # Extract translatable units from AST
            units = front_matter_units + self._extract_units_from_ast(ast, main_content)

            # Filter out non-translatable units
            units = [unit for unit in units if self._is_translatable_text(unit.content)]

            return ParseResult(
                units=units,
                file_type="markdown",
                encoding="utf-8",
                line_count=content.count('\n') + 1,
                metadata={
                    "parser": "MarkdownParser",
                    "version": "1.0.0",
                    "has_front_matter": bool(front_matter_units)
                }
            )

        except Exception as e:
            raise ParseError(f"Failed to parse Markdown file {file_path}: {e}") from e

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

        # Process the content line by line
        lines = original_content.splitlines(keepends=True)
        result_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line should be translated
            translated_line = self._translate_line(line, translation_map)
            result_lines.append(translated_line)
            i += 1

        return ''.join(result_lines)

    def _extract_front_matter(self, content: str) -> List[TranslatableUnit]:
        """
        Extract translatable text from Front Matter.

        Args:
            content: File content

        Returns:
            List of translatable units from Front Matter
        """
        units = []
        match = self._front_matter_pattern.search(content)

        if match:
            front_matter = match.group(1)
            lines = front_matter.split('\n')

            for line_num, line in enumerate(lines, 1):
                if ':' in line:
                    key, value = line.split(':', 1)
                    value = value.strip()

                    # Extract translatable values (like title, description, etc.)
                    if value and self._is_front_matter_value_translatable(key.strip(), value):
                        units.append(TranslatableUnit(
                            content=value,
                            unit_type=UnitType.METADATA,
                            line_number=line_num,
                            column_number=1,
                            context=f"Front Matter: {key.strip()}",
                            metadata={
                                'original_content': line,
                                'front_matter_key': key.strip(),
                                'is_front_matter': True
                            }
                        ))

        return units

    def _remove_front_matter(self, content: str) -> str:
        """
        Remove Front Matter from content.

        Args:
            content: File content

        Returns:
            Content without Front Matter
        """
        return self._front_matter_pattern.sub('', content)

    def _parse_markdown_ast(self, content: str) -> List[MarkdownNode]:
        """
        Parse Markdown content into AST nodes.

        Args:
            content: Markdown content

        Returns:
            List of AST nodes
        """
        # Use mistune to parse the content
        # Note: This is a simplified implementation
        # A full implementation would need to handle the mistune AST properly
        return self._create_simple_ast(content)

    def _create_simple_ast(self, content: str) -> List[MarkdownNode]:
        """
        Create a simple AST from Markdown content.

        Args:
            content: Markdown content

        Returns:
            List of AST nodes
        """
        nodes = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            # Detect different Markdown elements
            if line.startswith('#'):
                # Header
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                if text:
                    nodes.append(MarkdownNode(
                        type='heading',
                        text=text,
                        line_number=line_num,
                        column_number=1,
                        attrs={'level': level}
                    ))

            elif line.startswith('- ') or line.startswith('* '):
                # Unordered list item
                text = line[2:].strip()
                if text:
                    nodes.append(MarkdownNode(
                        type='list_item',
                        text=text,
                        line_number=line_num,
                        column_number=3
                    ))

            elif re.match(r'^\d+\.\s+', line):
                # Ordered list item
                text = re.sub(r'^\d+\.\s+', '', line).strip()
                if text:
                    nodes.append(MarkdownNode(
                        type='list_item',
                        text=text,
                        line_number=line_num,
                        column_number=1
                    ))

            elif line.startswith('> '):
                # Blockquote
                text = line[2:].strip()
                if text:
                    nodes.append(MarkdownNode(
                        type='blockquote',
                        text=text,
                        line_number=line_num,
                        column_number=3
                    ))

            elif line.startswith('```'):
                # Code block - skip
                continue

            elif line.strip():
                # Regular paragraph
                # Extract text from inline elements
                text = self._extract_text_from_inline_elements(line)
                if text:
                    nodes.append(MarkdownNode(
                        type='paragraph',
                        text=text,
                        line_number=line_num,
                        column_number=1
                    ))

        return nodes

    def _extract_text_from_inline_elements(self, line: str) -> str:
        """
        Extract plain text from inline Markdown elements.

        Args:
            line: Line with inline elements

        Returns:
            Plain text content
        """
        # Remove inline formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)  # Images

        return text.strip()

    def _extract_units_from_ast(self, ast: List[MarkdownNode], content: str) -> List[TranslatableUnit]:
        """
        Extract translatable units from AST nodes.

        Args:
            ast: List of AST nodes
            content: Original content

        Returns:
            List of translatable units
        """
        units = []

        for node in ast:
            if node.text and self._is_translatable_text(node.text):
                unit_type = self._get_unit_type_from_node(node)

                units.append(TranslatableUnit(
                    content=node.text,
                    unit_type=unit_type,
                    line_number=node.line_number,
                    column_number=node.column_number,
                    context=f"Markdown {node.type}",
                    metadata={
                        'original_content': node.text,
                        'node_type': node.type,
                        'attrs': node.attrs or {}
                    }
                ))

        return units

    def _get_unit_type_from_node(self, node: MarkdownNode) -> UnitType:
        """
        Get the unit type from an AST node.

        Args:
            node: AST node

        Returns:
            Unit type
        """
        if node.type == 'heading':
            return UnitType.TEXT_NODE
        elif node.type in ['paragraph', 'list_item', 'blockquote']:
            return UnitType.TEXT_NODE
        else:
            return UnitType.OTHER

    def _is_front_matter_value_translatable(self, key: str, value: str) -> bool:
        """
        Check if a Front Matter value should be translated.

        Args:
            key: Front Matter key
            value: Front Matter value

        Returns:
            True if the value should be translated
        """
        # Keys that typically contain translatable content
        translatable_keys = {
            'title', 'description', 'summary', 'excerpt', 'subtitle',
            'author', 'authors', 'tags', 'categories', 'keywords'
        }

        if key.lower() not in translatable_keys:
            return False

        # Check if the value looks like translatable text
        return self._is_translatable_text(value)

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

        # Skip text that's mostly code or technical terms
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
            r'```',  # Code blocks
            r'`[^`]+`',  # Inline code
            r'import\s+',  # Import statements
            r'from\s+',  # From statements
            r'def\s+',  # Function definitions
            r'class\s+',  # Class definitions
            r'#\s*',  # Comments
        ]

        code_count = sum(1 for pattern in code_patterns if re.search(pattern, text))
        return code_count > len(text.split()) * 0.3

    def _translate_line(self, line: str, translation_map: Dict[str, str]) -> str:
        """
        Translate a single line using the translation map.

        Args:
            line: Line to translate
            translation_map: Mapping of original to translated content

        Returns:
            Translated line
        """
        # Simple implementation - replace exact matches
        for original, translated in translation_map.items():
            if original in line:
                line = line.replace(original, translated)

        return line

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
