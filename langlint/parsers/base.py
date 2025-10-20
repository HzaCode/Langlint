"""
Base parser classes and interfaces.

This module defines the abstract base classes that all parsers must implement
to ensure a consistent interface across different file type parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class UnitType(Enum):
    """Types of translatable units."""
    COMMENT = "comment"
    DOCSTRING = "docstring"
    STRING_LITERAL = "string_literal"
    TEXT_NODE = "text_node"
    METADATA = "metadata"
    OTHER = "other"


@dataclass
class TranslatableUnit:
    """
    Represents a unit of text that can be translated.

    Attributes:
        content: The actual text content to be translated
        unit_type: The type of translatable unit
        line_number: Line number where this unit appears (1-indexed)
        column_number: Column number where this unit starts (1-indexed)
        context: Additional context information about this unit
        metadata: Extra metadata specific to the file type
    """
    content: str
    unit_type: UnitType
    line_number: int
    column_number: int
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate the unit after initialization."""
        if not self.content.strip():
            raise ValueError("TranslatableUnit content cannot be empty")
        if self.line_number < 1:
            raise ValueError("Line number must be >= 1")
        if self.column_number < 1:
            raise ValueError("Column number must be >= 1")


@dataclass
class ParseResult:
    """
    Result of parsing a file for translatable units.

    Attributes:
        units: List of translatable units found in the file
        file_type: The detected file type
        encoding: The file encoding used
        line_count: Total number of lines in the file
        metadata: Additional file-level metadata
    """
    units: List[TranslatableUnit]
    file_type: str
    encoding: str
    line_count: int
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate the parse result after initialization."""
        if self.line_count < 0:
            raise ValueError("Line count must be >= 0")


class Parser(ABC):
    """
    Abstract base class for all file parsers.

    All parsers must implement the methods defined in this class to ensure
    a consistent interface across different file type parsers.
    """

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        Return a list of file extensions this parser supports.

        Returns:
            List of file extensions (e.g., ['.py', '.pyi'])
        """
        pass

    @property
    @abstractmethod
    def supported_mime_types(self) -> List[str]:
        """
        Return a list of MIME types this parser supports.

        Returns:
            List of MIME types (e.g., ['text/x-python', 'application/x-python-code'])
        """
        pass

    @abstractmethod
    def can_parse(self, file_path: str, content: Optional[str] = None) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file
            content: Optional file content (if already loaded)

        Returns:
            True if this parser can handle the file, False otherwise
        """
        pass

    @abstractmethod
    def extract_translatable_units(self, content: str, file_path: str) -> ParseResult:
        """
        Extract translatable units from file content.

        Args:
            content: The file content to parse
            file_path: Path to the file (for context)

        Returns:
            ParseResult containing all translatable units found

        Raises:
            ParseError: If the file cannot be parsed
            ValueError: If the content is invalid
        """
        pass

    @abstractmethod
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
            file_path: Path to the file (for context)

        Returns:
            The reconstructed file content with translations applied

        Raises:
            ReconstructionError: If the file cannot be reconstructed
            ValueError: If the translated units are invalid
        """
        pass

    def validate_units(self, units: List[TranslatableUnit]) -> None:
        """
        Validate a list of translatable units.

        Args:
            units: List of units to validate

        Raises:
            ValueError: If any unit is invalid
        """
        for i, unit in enumerate(units):
            if not isinstance(unit, TranslatableUnit):
                raise ValueError(f"Unit {i} is not a TranslatableUnit instance")
            if not unit.content.strip():
                raise ValueError(f"Unit {i} has empty content")
            if unit.line_number < 1:
                raise ValueError(f"Unit {i} has invalid line number: {unit.line_number}")
            if unit.column_number < 1:
                raise ValueError(f"Unit {i} has invalid column number: {unit.column_number}")


class ParseError(Exception):
    """Exception raised when a file cannot be parsed."""
    pass


class ReconstructionError(Exception):
    """Exception raised when a file cannot be reconstructed."""
    pass
