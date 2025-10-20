"""
Jupyter Notebook parser for extracting translatable text from .ipynb files.

This parser uses nbformat to parse Notebook JSON structure and recursively
processes code cells with Python parser and Markdown cells with Markdown parser.
"""

import json
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass

try:
    import nbformat
    from nbformat import NotebookNode
except ImportError:
    nbformat = None
    NotebookNode = None

from .base import Parser, TranslatableUnit, ParseResult, UnitType, ParseError
from .python_parser import PythonParser
from .markdown_parser import MarkdownParser


@dataclass
class NotebookCell:
    """Represents a Jupyter Notebook cell."""
    cell_type: str
    source: str
    metadata: Dict[str, Any]
    outputs: Optional[List[Dict[str, Any]]] = None
    execution_count: Optional[int] = None


class NotebookParser(Parser):
    """
    Parser for Jupyter Notebook files that processes different cell types.

    This parser uses nbformat to parse the Notebook JSON structure and
    recursively processes code cells with Python parser and Markdown cells
    with Markdown parser.
    """

    def __init__(self):
        """Initialize the Notebook parser."""
        if nbformat is None:
            raise ImportError("nbformat is required for Notebook parsing. Install with: pip install nbformat")

        self.python_parser = PythonParser()
        self.markdown_parser = MarkdownParser()

    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions."""
        return ['.ipynb']

    @property
    def supported_mime_types(self) -> List[str]:
        """Return supported MIME types."""
        return [
            'application/x-ipynb+json',
            'application/json'
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

        # Check if content is valid JSON and looks like a Notebook
        try:
            data = json.loads(content)
            return (
                isinstance(data, dict) and
                'cells' in data and
                'metadata' in data and
                'nbformat' in data
            )
        except (json.JSONDecodeError, TypeError):
            return False

    def extract_translatable_units(self, content: str, file_path: str) -> ParseResult:
        """
        Extract translatable units from Jupyter Notebook content.

        Args:
            content: The file content to parse
            file_path: Path to the file

        Returns:
            ParseResult containing all translatable units found

        Raises:
            ParseError: If the file cannot be parsed
        """
        try:
            # Parse the Notebook
            notebook = nbformat.reads(content, as_version=4)

            # Extract translatable units from all cells
            units = []
            total_lines = 0

            for cell_index, cell in enumerate(notebook.cells):
                cell_units = self._extract_units_from_cell(cell, cell_index, file_path)
                units.extend(cell_units)
                total_lines += len(cell.source.split('\n'))

            # Add notebook metadata units
            metadata_units = self._extract_metadata_units(notebook.metadata, file_path)
            units.extend(metadata_units)

            return ParseResult(
                units=units,
                file_type="jupyter_notebook",
                encoding="utf-8",
                line_count=total_lines,
                metadata={
                    "parser": "NotebookParser",
                    "version": "1.0.0",
                    "nbformat": notebook.nbformat,
                    "nbformat_minor": notebook.nbformat_minor,
                    "cell_count": len(notebook.cells)
                }
            )

        except Exception as e:
            raise ParseError(f"Failed to parse Jupyter Notebook {file_path}: {e}") from e

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
        try:
            # Parse the original notebook
            notebook = nbformat.reads(original_content, as_version=4)

            # Group translated units by cell
            units_by_cell = self._group_units_by_cell(translated_units)

            # Process each cell
            for cell_index, cell in enumerate(notebook.cells):
                if cell_index in units_by_cell:
                    cell_units = units_by_cell[cell_index]
                    cell.source = self._reconstruct_cell_source(cell, cell_units)

            # Convert back to JSON
            return nbformat.writes(notebook)

        except Exception as e:
            raise ParseError(f"Failed to reconstruct Jupyter Notebook {file_path}: {e}") from e

    def _extract_units_from_cell(self, cell: NotebookNode, cell_index: int, file_path: str) -> List[TranslatableUnit]:
        """
        Extract translatable units from a notebook cell.

        Args:
            cell: Notebook cell
            cell_index: Index of the cell
            file_path: Path to the file

        Returns:
            List of translatable units from the cell
        """
        units = []

        if cell.cell_type == 'code':
            # Process code cell with Python parser
            source = self._get_cell_source(cell)
            if source.strip():
                try:
                    parse_result = self.python_parser.extract_translatable_units(source, file_path)
                    # Adjust line numbers to account for cell position
                    for unit in parse_result.units:
                        unit.line_number += cell_index * 10  # Approximate offset
                        unit.metadata = unit.metadata or {}
                        unit.metadata.update({
                            'cell_index': cell_index,
                            'cell_type': 'code',
                            'notebook_file': file_path
                        })
                    units.extend(parse_result.units)
                except Exception:
                    # If Python parsing fails, skip this cell
                    pass

        elif cell.cell_type == 'markdown':
            # Process markdown cell with Markdown parser
            source = self._get_cell_source(cell)
            if source.strip():
                try:
                    parse_result = self.markdown_parser.extract_translatable_units(source, file_path)
                    # Adjust line numbers to account for cell position
                    for unit in parse_result.units:
                        unit.line_number += cell_index * 10  # Approximate offset
                        unit.metadata = unit.metadata or {}
                        unit.metadata.update({
                            'cell_index': cell_index,
                            'cell_type': 'markdown',
                            'notebook_file': file_path
                        })
                    units.extend(parse_result.units)
                except Exception:
                    # If Markdown parsing fails, skip this cell
                    pass

        elif cell.cell_type == 'raw':
            # Process raw cell - extract text content
            source = self._get_cell_source(cell)
            if source.strip() and self._is_translatable_text(source):
                units.append(TranslatableUnit(
                    content=source.strip(),
                    unit_type=UnitType.TEXT_NODE,
                    line_number=cell_index * 10 + 1,
                    column_number=1,
                    context=f"Raw cell {cell_index}",
                    metadata={
                        'cell_index': cell_index,
                        'cell_type': 'raw',
                        'notebook_file': file_path,
                        'original_content': source
                    }
                ))

        return units

    def _extract_metadata_units(self, metadata: Dict[str, Any], file_path: str) -> List[TranslatableUnit]:
        """
        Extract translatable units from notebook metadata.

        Args:
            metadata: Notebook metadata
            file_path: Path to the file

        Returns:
            List of translatable units from metadata
        """
        units = []

        # Extract from common metadata fields
        translatable_fields = {
            'title', 'description', 'summary', 'tags', 'keywords',
            'authors', 'author', 'subtitle'
        }

        for key, value in metadata.items():
            if key.lower() in translatable_fields and isinstance(value, str):
                if value.strip() and self._is_translatable_text(value):
                    units.append(TranslatableUnit(
                        content=value.strip(),
                        unit_type=UnitType.METADATA,
                        line_number=1,
                        column_number=1,
                        context=f"Notebook metadata: {key}",
                        metadata={
                            'metadata_key': key,
                            'notebook_file': file_path,
                            'original_content': value,
                            'is_notebook_metadata': True
                        }
                    ))

        return units

    def _get_cell_source(self, cell: NotebookNode) -> str:
        """
        Get the source content from a cell.

        Args:
            cell: Notebook cell

        Returns:
            Cell source as string
        """
        if isinstance(cell.source, list):
            return ''.join(cell.source)
        return str(cell.source)

    def _group_units_by_cell(self, units: List[TranslatableUnit]) -> Dict[int, List[TranslatableUnit]]:
        """
        Group translated units by cell index.

        Args:
            units: List of translated units

        Returns:
            Dictionary mapping cell index to units
        """
        units_by_cell = {}

        for unit in units:
            if unit.metadata and 'cell_index' in unit.metadata:
                cell_index = unit.metadata['cell_index']
                if cell_index not in units_by_cell:
                    units_by_cell[cell_index] = []
                units_by_cell[cell_index].append(unit)

        return units_by_cell

    def _reconstruct_cell_source(self, cell: NotebookNode, units: List[TranslatableUnit]) -> str:
        """
        Reconstruct cell source with translated units.

        Args:
            cell: Original cell
            units: Translated units for this cell

        Returns:
            Reconstructed cell source
        """
        source = self._get_cell_source(cell)

        if cell.cell_type == 'code':
            # Use Python parser to reconstruct
            return self.python_parser.reconstruct_file(source, units, "")

        elif cell.cell_type == 'markdown':
            # Use Markdown parser to reconstruct
            return self.markdown_parser.reconstruct_file(source, units, "")

        elif cell.cell_type == 'raw':
            # Simple text replacement for raw cells
            for unit in units:
                if unit.metadata and 'original_content' in unit.metadata:
                    original = unit.metadata['original_content']
                    source = source.replace(original, unit.content)
            return source

        return source

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
            'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
            'try:', 'except:', 'finally:', 'with ', 'as ', 'return ',
            '=', '==', '!=', '<=', '>=', 'and ', 'or ', 'not ',
            '(', ')', '[', ']', '{', '}', ':', ';', '\\',
            '```', '`', 'plt.', 'df.', 'np.', 'pd.'
        ]

        text_lower = text.lower()
        code_count = sum(1 for pattern in code_patterns if pattern in text_lower)

        # If more than 30% of the text matches code patterns, consider it code
        return code_count > len(text.split()) * 0.3
