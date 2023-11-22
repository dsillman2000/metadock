from functools import cached_property
import os
from pathlib import Path
from typing import Any, Optional
from enum import auto, StrEnum
import jinja2
import pydantic
from metadock import exceptions
from metadock.target_formats import MetadockTargetFormat, MetadockTargetFormatFactory
import yaml
import fnmatch
import shutil


class ValidationStatus(StrEnum):
    SUCCESS = auto()
    FAILURE = auto()
    WARNING = auto()


class MetadockProjectValidationResult(pydantic.BaseModel):
    status: ValidationStatus = ValidationStatus.SUCCESS
    failures: list[str] = []
    warnings: list[str] = []

    def append_warning(self, warning_msg: str):
        if self.status == ValidationStatus.SUCCESS.value:
            self.status = ValidationStatus.WARNING
        self.warnings.append(warning_msg)

    def append_failure(self, failure_msg: str):
        if self.status != ValidationStatus.FAILURE.value:
            self.status = ValidationStatus.FAILURE
        self.failures.append(failure_msg)

    @property
    def ok(self) -> bool:
        return self.status.value in (ValidationStatus.SUCCESS, ValidationStatus.WARNING)


class MetadockProject:
    directory: Path

    def __init__(self, directory: Path | str):
        self.directory = Path(directory)

    @cached_property
    def templated_documents_directory(self) -> Path:
        return self.directory / "templated_documents"

    @cached_property
    def templated_documents(self) -> dict[str, "MetadockTemplatedDocument"]:
        template_objects = self.templated_documents_directory.glob("**/*.*")
        relative_template_files: list[Path] = list(
            tmpl.relative_to(self.templated_documents_directory) for tmpl in template_objects if tmpl.is_file()
        )
        return {
            str(relative_template_file): MetadockTemplatedDocument.from_project_relative_path(
                self.directory, relative_template_file
            )
            for relative_template_file in relative_template_files
        }

    @cached_property
    def content_schematics_directory(self) -> Path:
        return self.directory / "content_schematics"

    @cached_property
    def content_schematics(self) -> dict[str, "MetadockContentSchematic"]:
        content_schematic_ymls = self.content_schematics_directory.glob("**/*.yml")
        content_schematics: dict[str, MetadockContentSchematic] = {}

        for content_schematic_yml in content_schematic_ymls:
            schematics = MetadockContentSchematic.collect_from_file(content_schematic_yml)
            for schematic in schematics:
                if schematic.name in content_schematics:
                    raise exceptions.MetadockContentSchematicParsingException(
                        "Got non-unique 'name' key: %s" % schematic.name
                    )
                content_schematics[schematic.name] = schematic

        return content_schematics

    @cached_property
    def generated_documents_directory(self) -> Path:
        return self.directory / "generated_documents"

    def build(self, schematics: Optional[list[str]] = None):
        if schematics is None:
            schematics = list(self.content_schematics.keys())

        for schematic_name in schematics:
            content_schematic = self.content_schematics[schematic_name]
            compiled_targets = content_schematic.to_compiled_targets(self)

            for target_format, compiled_document in compiled_targets.items():
                file_extension = MetadockTargetFormatFactory.target_format(target_format).file_extension
                generated_filepath = self.generated_documents_directory / (schematic_name + "." + file_extension)
                with generated_filepath.open("w") as handle:
                    handle.write(str(compiled_document))

    def clean(self):
        """Deletes all generated documents in the `generated_documents` project directory."""
        shutil.rmtree(self.generated_documents_directory)
        os.makedirs(self.generated_documents_directory)

    def validate(self) -> MetadockProjectValidationResult:
        validation_result = MetadockProjectValidationResult()

        if not self.directory.exists():
            validation_result.append_failure("Could not find .metadock directory: %s" % self.directory)
            return validation_result

        if not self.templated_documents_directory.exists():
            validation_result.append_warning(
                "Could not find .metadock/templated_documents directory. No templates will be used in compilation."
            )

        if not self.content_schematics_directory.exists():
            validation_result.append_warning(
                "Could not find .metadock/content_schematics directory. No content will be used in compilation."
            )

        if not self.generated_documents_directory.exists():
            validation_result.append_warning(
                "Could not find .metadock/generated_documents directory. Creating empty directory now."
            )
            os.makedirs(self.generated_documents_directory)

        return validation_result

    def list(self, schematic_globs: list[str] = [], template_globs: list[str] = []) -> list[str]:
        schematics: list[str] = []
        for schematic_glob in schematic_globs:
            schematics += self._query_schematics_by_name_glob(schematic_glob)
        for template_glob in template_globs:
            schematics += self._query_schematics_by_template_glob(template_glob)
        return list(set((schematics)))

    def _query_schematics_by_name_glob(self, schematic_glob: str) -> "list[str]":
        return [
            schematic_name
            for schematic_name in self.content_schematics
            if fnmatch.fnmatch(schematic_name, schematic_glob)
        ]

    def _query_schematics_by_template_glob(self, template_glob: str) -> "list[str]":
        return [
            schematic.name
            for schematic in self.content_schematics.values()
            if fnmatch.fnmatch(schematic.template, template_glob)
        ]


class MetadockTemplatedDocument(pydantic.BaseModel):
    absolute_path: Path
    project_relative_path: Path

    @classmethod
    def from_absolute_path(cls, absolute_path: Path | str):
        absolute_path = Path(absolute_path)

        if "/.metadock/templated_documents/" not in str(absolute_path):
            raise exceptions.MetadockProjectException("TemplatedDocument appears not to be in metadock project dir.")

        project_relative_path = Path(str(absolute_path).split("/.metadock/templated_documents/")[1])
        cls(absolute_path=absolute_path, project_relative_path=project_relative_path)

    @classmethod
    def from_project_relative_path(
        cls, project_dir: Path | str, project_relative_path: Path | str
    ) -> "MetadockTemplatedDocument":
        project_relative_path = Path(project_relative_path)
        absolute_path = Path(project_dir) / "templated_documents" / Path(project_relative_path)
        return cls(absolute_path=absolute_path, project_relative_path=project_relative_path)

    def content(self) -> str:
        with self.absolute_path.open("r") as handle:
            return handle.read()

    def jinja_template(self) -> jinja2.Template:
        try:
            return jinja2.Template(self.content())
        except Exception as e:
            raise exceptions.MetadockTemplateParsingException(
                "Failed to parse jinja2.Template from %s,\n\tdue to exception:\n%s"
                % (self.project_relative_path, str(e))
            )


class MetadockContentSchematic(pydantic.BaseModel):
    name: str
    template: str
    target_formats: list[str]
    context: Any = {}

    def to_compiled_targets(self, project: MetadockProject) -> dict[str, str | bytes]:
        compiled_targets: dict[str, str | bytes] = {}

        for target_format in self.target_formats:
            target_format = MetadockTargetFormatFactory.target_format(target_format)
            templated_document = project.templated_documents[self.template]
            rendered_document = templated_document.jinja_template().render(self.context)
            post_processed_document = target_format.handler(rendered_document)

            compiled_targets[target_format.identifier] = post_processed_document

        return compiled_targets

    @classmethod
    def collect_from_file(cls, yaml_path: Path | str) -> "list[MetadockContentSchematic]":
        yaml_path = Path(yaml_path)
        content_schematics: list[MetadockContentSchematic] = []

        if not yaml_path.exists():
            raise exceptions.MetadockContentSchematicParsingException(
                "Coud not find content schematic file %s" % yaml_path
            )

        with yaml_path.open("r") as handle:
            yaml_contents: dict = yaml.load(handle, yaml.BaseLoader)

        defined_schematics = yaml_contents.get("content_schematics", [])
        required_keys = ["name", "target_formats", "template"]

        for def_schematic in defined_schematics:
            for req_key in required_keys:
                if not def_schematic.get(req_key):
                    raise exceptions.MetadockContentSchematicParsingException(
                        "Missing required key for content schematic in %s: '%s'" % (yaml_path, req_key)
                    )
            content_schematics.append(
                cls(
                    name=def_schematic["name"],
                    template=def_schematic["template"],
                    target_formats=def_schematic["target_formats"],
                    context=def_schematic.get("context", {}),
                )
            )

        return content_schematics
