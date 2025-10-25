"""
Configuration file parser for extracting translatable text from config files.

This parser intelligently identifies and translates line-end comments and
descriptive string values in various configuration file formats.
"""

import re
import json
import yaml
import toml
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass

from .base import Parser, TranslatableUnit, ParseResult, UnitType, ParseError


@dataclass
class ConfigSchema:
    """Represents a configuration schema for identifying translatable fields."""
    translatable_keys: List[str]
    translatable_values: List[str]
    comment_patterns: List[str]
    value_patterns: List[str]


class ConfigParser(Parser):
    """
    Parser for configuration files that extracts translatable text.

    This parser intelligently identifies and extracts line-end comments
    and descriptive string values from various configuration file formats
    including YAML, TOML, JSON, INI, and others.
    """

    # Configuration schemas for different file types
    CONFIG_SCHEMAS = {
        '.yaml': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=['#'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*["\']([^"\']+)["\']']
        ),
        '.yml': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=['#'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*["\']([^"\']+)["\']']
        ),
        '.toml': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=['#'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\']([^"\']+)["\']']
        ),
        '.json': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=[],  # JSON doesn't support comments
            value_patterns=[r'["\']([a-zA-Z_][a-zA-Z0-9_]*?)["\']\s*:\s*["\']([^"\']+)["\']']
        ),
        '.ini': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=[';', '#'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\']?([^"\'\n]+)["\']?']
        ),
        '.cfg': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=[';', '#'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\']?([^"\'\n]+)["\']?']
        ),
        '.conf': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=['#'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*["\']?([^"\'\n]+)["\']?']
        ),
        '.properties': ConfigSchema(
            translatable_keys=['title', 'description', 'summary', 'name', 'label'],
            translatable_values=['description', 'summary', 'title', 'name', 'label', 'help', 'message'],
            comment_patterns=['#', '!'],
            value_patterns=[r'^\s*[a-zA-Z_][a-zA-Z0-9_.]*\s*=\s*([^\n]+)']
        ),
    }

    def __init__(self):
        """Initialize the configuration parser."""
        # Pre-compile regular expressions for better performance
        self._compiled_patterns = {}
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regular expressions for all supported configuration types."""
        for ext, schema in self.CONFIG_SCHEMAS.items():
            compiled = {}

            # Compile comment patterns
            compiled['comments'] = []
            for pattern in schema.comment_patterns:
                escaped = re.escape(pattern)
                regex = rf'^\s*{escaped}\s*(.*)$'
                compiled['comments'].append(re.compile(regex, re.MULTILINE))

            # Compile value patterns
            compiled['values'] = []
            for pattern in schema.value_patterns:
                compiled['values'].append(re.compile(pattern, re.MULTILINE))

            self._compiled_patterns[ext] = compiled

    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions."""
        return list(self.CONFIG_SCHEMAS.keys())

    @property
    def supported_mime_types(self) -> List[str]:
        """Return supported MIME types."""
        return [
            'text/x-yaml',
            'text/yaml',
            'application/x-yaml',
            'application/yaml',
            'text/x-toml',
            'text/toml',
            'application/x-toml',
            'application/toml',
            'application/json',
            'text/x-ini',
            'text/ini',
            'application/x-ini',
            'application/ini',
            'text/x-properties',
            'text/properties',
            'application/x-properties',
            'application/properties',
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

        # Check if content looks like a configuration file
        if not content.strip():
            return False

        # Try to parse the content based on file extension
        ext = self._get_file_extension(file_path)
        if ext not in self.CONFIG_SCHEMAS:
            return False

        try:
            if ext in ['.yaml', '.yml']:
                yaml.safe_load(content)
            elif ext == '.toml':
                toml.loads(content)
            elif ext == '.json':
                json.loads(content)
            elif ext in ['.ini', '.cfg', '.conf', '.properties']:
                # Simple check for key=value format
                return '=' in content
            return True
        except Exception:
            return False

    def extract_translatable_units(self, content: str, file_path: str) -> ParseResult:
        """
        Extract translatable units from configuration file content.

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
            if ext not in self.CONFIG_SCHEMAS:
                raise ParseError(f"Unsupported configuration file extension: {ext}")

            # Get schema for this file type
            schema = self.CONFIG_SCHEMAS[ext]
            compiled = self._compiled_patterns[ext]

            # Extract translatable units
            units = []

            # Extract comments
            for regex in compiled['comments']:
                for match in regex.finditer(content):
                    comment_text = match.group(1).strip()
                    if comment_text and self._is_translatable_text(comment_text):
                        line_num = content[:match.start()].count('\n') + 1
                        col_num = match.start() - content.rfind('\n', 0, match.start()) - 1

                        units.append(TranslatableUnit(
                            content=comment_text,
                            unit_type=UnitType.COMMENT,
                            line_number=line_num,
                            column_number=col_num,
                            context=f"Configuration comment in {ext} file",
                            metadata={
                                'original_content': match.group(0),
                                'file_extension': ext,
                                'comment_type': 'line_end'
                            }
                        ))

            # Extract translatable values
            for regex in compiled['values']:
                for match in regex.finditer(content):
                    if len(match.groups()) >= 2:
                        # Pattern with key and value groups
                        key = match.group(1)
                        value = match.group(2)

                        if (self._is_translatable_key(key, schema) and
                            value and self._is_translatable_text(value)):

                            line_num = content[:match.start()].count('\n') + 1
                            col_num = match.start() - content.rfind('\n', 0, match.start()) - 1

                            units.append(TranslatableUnit(
                                content=value,
                                unit_type=UnitType.METADATA,
                                line_number=line_num,
                                column_number=col_num,
                                context=f"Configuration value for '{key}' in {ext} file",
                                metadata={
                                    'original_content': match.group(0),
                                    'file_extension': ext,
                                    'config_key': key,
                                    'value_type': 'descriptive'
                                }
                            ))
                    else:
                        # Pattern with only value group
                        value = match.group(1)

                        if value and self._is_translatable_text(value):
                            line_num = content[:match.start()].count('\n') + 1
                            col_num = match.start() - content.rfind('\n', 0, match.start()) - 1

                            units.append(TranslatableUnit(
                                content=value,
                                unit_type=UnitType.METADATA,
                                line_number=line_num,
                                column_number=col_num,
                                context=f"Configuration value in {ext} file",
                                metadata={
                                    'original_content': match.group(0),
                                    'file_extension': ext,
                                    'value_type': 'descriptive'
                                }
                            ))

            # Extract from structured data if possible
            structured_units = self._extract_from_structured_data(content, ext, file_path)
            units.extend(structured_units)

            return ParseResult(
                units=units,
                file_type="configuration",
                encoding="utf-8",
                line_count=content.count('\n') + 1,
                metadata={
                    "parser": "ConfigParser",
                    "version": "1.0.0",
                    "file_extension": ext,
                    "config_type": self._get_config_type_name(ext)
                }
            )

        except Exception as e:
            raise ParseError(f"Failed to parse configuration file {file_path}: {e}") from e

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

        # Replace content in the file
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
            File extension (e.g., '.yaml')
        """
        return '.' + file_path.split('.')[-1].lower()

    def _extract_from_structured_data(
        self,
        content: str,
        ext: str,
        file_path: str
    ) -> List[TranslatableUnit]:
        """
        Extract translatable units from structured configuration data.

        Args:
            content: File content
            ext: File extension
            file_path: Path to the file

        Returns:
            List of translatable units from structured data
        """
        units = []

        try:
            if ext in ['.yaml', '.yml']:
                data = yaml.safe_load(content)
                units.extend(self._extract_from_yaml_data(data, file_path))
            elif ext == '.toml':
                data = toml.loads(content)
                units.extend(self._extract_from_toml_data(data, file_path))
            elif ext == '.json':
                data = json.loads(content)
                units.extend(self._extract_from_json_data(data, file_path))
        except Exception:
            # If structured parsing fails, return empty list
            pass

        return units

    def _extract_from_yaml_data(
        self,
        data: Any,
        file_path: str,
        path: str = ""
    ) -> List[TranslatableUnit]:
        """
        Extract translatable units from YAML data.

        Args:
            data: YAML data
            file_path: Path to the file
            path: Current path in the data structure

        Returns:
            List of translatable units
        """
        units = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, str) and self._is_translatable_text(value):
                    units.append(TranslatableUnit(
                        content=value,
                        unit_type=UnitType.METADATA,
                        line_number=1,  # Approximate
                        column_number=1,
                        context=f"YAML value at {current_path}",
                        metadata={
                            'original_content': value,
                            'file_extension': '.yaml',
                            'config_key': current_path,
                            'value_type': 'structured'
                        }
                    ))
                elif isinstance(value, (dict, list)):
                    units.extend(self._extract_from_yaml_data(value, file_path, current_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"

                if isinstance(item, str) and self._is_translatable_text(item):
                    units.append(TranslatableUnit(
                        content=item,
                        unit_type=UnitType.METADATA,
                        line_number=1,  # Approximate
                        column_number=1,
                        context=f"YAML array item at {current_path}",
                        metadata={
                            'original_content': item,
                            'file_extension': '.yaml',
                            'config_key': current_path,
                            'value_type': 'structured'
                        }
                    ))
                elif isinstance(item, (dict, list)):
                    units.extend(self._extract_from_yaml_data(item, file_path, current_path))

        return units

    def _extract_from_toml_data(
        self,
        data: Any,
        file_path: str,
        path: str = ""
    ) -> List[TranslatableUnit]:
        """
        Extract translatable units from TOML data.

        Args:
            data: TOML data
            file_path: Path to the file
            path: Current path in the data structure

        Returns:
            List of translatable units
        """
        units = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, str) and self._is_translatable_text(value):
                    units.append(TranslatableUnit(
                        content=value,
                        unit_type=UnitType.METADATA,
                        line_number=1,  # Approximate
                        column_number=1,
                        context=f"TOML value at {current_path}",
                        metadata={
                            'original_content': value,
                            'file_extension': '.toml',
                            'config_key': current_path,
                            'value_type': 'structured'
                        }
                    ))
                elif isinstance(value, (dict, list)):
                    units.extend(self._extract_from_toml_data(value, file_path, current_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"

                if isinstance(item, str) and self._is_translatable_text(item):
                    units.append(TranslatableUnit(
                        content=item,
                        unit_type=UnitType.METADATA,
                        line_number=1,  # Approximate
                        column_number=1,
                        context=f"TOML array item at {current_path}",
                        metadata={
                            'original_content': item,
                            'file_extension': '.toml',
                            'config_key': current_path,
                            'value_type': 'structured'
                        }
                    ))
                elif isinstance(item, (dict, list)):
                    units.extend(self._extract_from_toml_data(item, file_path, current_path))

        return units

    def _extract_from_json_data(
        self,
        data: Any,
        file_path: str,
        path: str = ""
    ) -> List[TranslatableUnit]:
        """
        Extract translatable units from JSON data.

        Args:
            data: JSON data
            file_path: Path to the file
            path: Current path in the data structure

        Returns:
            List of translatable units
        """
        units = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, str) and self._is_translatable_text(value):
                    units.append(TranslatableUnit(
                        content=value,
                        unit_type=UnitType.METADATA,
                        line_number=1,  # Approximate
                        column_number=1,
                        context=f"JSON value at {current_path}",
                        metadata={
                            'original_content': value,
                            'file_extension': '.json',
                            'config_key': current_path,
                            'value_type': 'structured'
                        }
                    ))
                elif isinstance(value, (dict, list)):
                    units.extend(self._extract_from_json_data(value, file_path, current_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"

                if isinstance(item, str) and self._is_translatable_text(item):
                    units.append(TranslatableUnit(
                        content=item,
                        unit_type=UnitType.METADATA,
                        line_number=1,  # Approximate
                        column_number=1,
                        context=f"JSON array item at {current_path}",
                        metadata={
                            'original_content': item,
                            'file_extension': '.json',
                            'config_key': current_path,
                            'value_type': 'structured'
                        }
                    ))
                elif isinstance(item, (dict, list)):
                    units.extend(self._extract_from_json_data(item, file_path, current_path))

        return units

    def _is_translatable_key(self, key: str, schema: ConfigSchema) -> bool:
        """
        Check if a configuration key should have translatable values.

        Args:
            key: Configuration key
            schema: Configuration schema

        Returns:
            True if the key should have translatable values
        """
        key_lower = key.lower()
        return any(translatable_key in key_lower for translatable_key in schema.translatable_keys)

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

        # Skip version numbers and technical identifiers
        if re.match(r'^v?\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?$', text.strip()):
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

    def _get_config_type_name(self, ext: str) -> str:
        """
        Get the human-readable configuration type name for a file extension.

        Args:
            ext: File extension

        Returns:
            Configuration type name
        """
        type_names = {
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.json': 'JSON',
            '.ini': 'INI',
            '.cfg': 'Configuration',
            '.conf': 'Configuration',
            '.properties': 'Properties',
        }

        return type_names.get(ext, 'Unknown')

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
