from typing import MutableMapping, Protocol, Type
import abc
import markdown

from metadock import exceptions


class MetadockTargetFormatFactory:
    _lookup: MutableMapping[str, "Type[MetadockTargetFormat]"] = {}

    @classmethod
    def register_target_format(cls, target_format: "Type[MetadockTargetFormat]"):
        cls._lookup[target_format.identifier] = target_format

    @classmethod
    def target_format(cls, identifier: str) -> "MetadockTargetFormat":
        if identifier not in cls._lookup:
            return PlaintextTargetFormat.from_file_extension(identifier)
        return cls._lookup[identifier]()


class TargetFormatHandler(Protocol):
    def __call__(self, rendered_document: str | bytes) -> str | bytes:
        ...


class MetadockTargetFormat(abc.ABC):
    file_extension: str
    identifier: str
    handler: TargetFormatHandler


class PlaintextTargetFormat(MetadockTargetFormat):
    file_extension: str
    identifier: str

    class _PlaintextTargetFormatHandler(TargetFormatHandler):
        def __call__(self, rendered_document: str | bytes) -> str | bytes:
            return rendered_document

    handler: TargetFormatHandler = _PlaintextTargetFormatHandler()

    def __init__(self, file_extension: str = ""):
        self.file_extension = file_extension
        self.identifier = file_extension

    @classmethod
    def from_file_extension(cls, file_extension: str) -> "PlaintextTargetFormat":
        return cls(file_extension=file_extension)


@MetadockTargetFormatFactory.register_target_format
class MdPlusHtmlTargetFormat(MetadockTargetFormat):
    file_extension: str = "html"
    identifier: str = "md+html"

    class _MdPlusHtmlTargetFormatHandler(TargetFormatHandler):
        def __call__(self, rendered_document: str | bytes) -> str | bytes:
            md = markdown.Markdown(extensions=["tables"])
            return md.convert(str(rendered_document))

    handler: TargetFormatHandler = _MdPlusHtmlTargetFormatHandler()
