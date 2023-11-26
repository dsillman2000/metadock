import abc
from typing import MutableMapping, Protocol, Type

import marko
from marko.ext.gfm import gfm

from metadock import exceptions


class MetadockTargetFormatFactory:
    """Lookup class for managing the mapping between string identifiers and their respective MetadockTargetFormat."""

    _lookup: MutableMapping[str, "Type[MetadockTargetFormat]"] = {}

    @classmethod
    def register_target_format(cls, target_format: "Type[MetadockTargetFormat]"):
        """Decorator function for registering a new MetadockTargetFormat using its classvar, `identifier` as the key.

        Args:
            target_format (Type[MetadockTargetFormat]): MetadockTargetFormat definition to register
        """
        cls._lookup[target_format.identifier] = target_format

    @classmethod
    def target_format(cls, identifier: str) -> "MetadockTargetFormat":
        """Lookup function for resolving a MetadockTargetFormat from its identifier. If no match is found, return a
        PlaintextTargetFormat with the provided identifier as a file extension.

        Args:
            identifier (str): Identifier for the target format to retrieve

        Returns:
            MetadockTargetFormat: Target format class for managing the exporting to a specific target format
        """
        if identifier not in cls._lookup:
            return PlaintextTargetFormat.from_file_extension(file_extension=identifier)
        return cls._lookup[identifier]()


class MetadockTargetFormat(abc.ABC):
    """Base class for representing the necessary interface for postprocessing a rendered document into a different
    target format.

    Attributes:
        file_extension (str): File extension to associate with this target format.
        identifier (str): String identifier for the target format, for lookup when parsing a content_schematics block.
    """

    file_extension: str
    identifier: str

    @classmethod
    @abc.abstractmethod
    def handler(cls, rendered_document: str | bytes) -> str | bytes:
        ...


class PlaintextTargetFormat(MetadockTargetFormat):
    """Fallback target format for writing the rendered document in plaintext. Performs no post-processing."""

    file_extension: str
    identifier: str

    @classmethod
    def handler(cls, rendered_document: str | bytes) -> str | bytes:
        """Returns its argument, unchanged.

        Args:
            rendered_document (str | bytes): Rendered document content to handle

        Returns:
            str | bytes: Plaintext representation of the rendered document
        """
        return rendered_document

    def __init__(self, file_extension: str = ""):
        """Instantiates a new PlaintextTargetFormat, enriched with a specific file_extension.

        Args:
            file_extension (str, optional): File extension to associate with this ad-hoc plaintext format.
                Defaults to the empty string.
        """
        self.file_extension = file_extension
        self.identifier = file_extension

    @classmethod
    def from_file_extension(cls, file_extension: str) -> "PlaintextTargetFormat":
        """Alias for the constructor, providing file_extension as a positional argument.

        Returns:
            PlaintextTargetFormat: A new instance of PlaintextTargetFormat, associated with the specific file_extension
                supplied.
        """
        return cls(file_extension=file_extension)


@MetadockTargetFormatFactory.register_target_format
class MdPlusHtmlTargetFormat(MetadockTargetFormat):
    """Canonical target format for producing HTML documents from a compiled Markdown document."""

    file_extension: str = "html"
    identifier: str = "md+html"

    @classmethod
    def handler(cls, rendered_document: str | bytes) -> str | bytes:
        """Parses the rendered document as a Markdown document, and converts it into plain HTML.

        Args:
            rendered_document (str | bytes): Rendered markdown document content to convert

        Returns:
            str | bytes: HTML markup of the original Markdown document
        """
        return gfm.convert(str(rendered_document))
