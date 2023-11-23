import fnmatch
import os
import shutil
from enum import StrEnum, auto
from functools import cached_property
from pathlib import Path
from typing import Any, Optional

import jinja2
import pydantic
import yaml

from metadock import exceptions, yaml_utils
from metadock.env import MetadockEnv
from metadock.target_formats import MetadockTargetFormat, MetadockTargetFormatFactory


class ValidationStatus(StrEnum):
    """Enumerated type for different top-level summary status values for project validation."""

    SUCCESS = auto()
    WARNING = auto()
    FAILURE = auto()


class MetadockProjectValidationResult(pydantic.BaseModel):
    """Project validation result pydantic Model.

    Attributes:
        status (ValidationStatus): Enumerated value for overall validation status
        failures (list[str]): List of failure messages emitted during validation
        warnings (list[str]): List of warnings emitted during validation
    """

    status: ValidationStatus = ValidationStatus.SUCCESS
    failures: list[str] = []
    warnings: list[str] = []

    def append_warning(self, warning_msg: str):
        """Interface for adding a warning to a running project validation result. Transitions the top-level status:

        SUCCESS -> WARNING
        WARNING -> WARNING
        FAILURE -> FAILURE

        Args:
            warning_msg (str): Message to associate with this warning.
        """
        if self.status == ValidationStatus.SUCCESS.value:
            self.status = ValidationStatus.WARNING
        self.warnings.append(warning_msg)

    def append_failure(self, failure_msg: str):
        """Interface for adding a failure to a running project validation result. Transitions the top-level status to
        FAILURE if it isn't already.

        Args:
            failure_msg (str): Message to associate with this failure.
        """
        if self.status != ValidationStatus.FAILURE.value:
            self.status = ValidationStatus.FAILURE
        self.failures.append(failure_msg)

    @property
    def ok(self) -> bool:
        """Whether or not this project passed validation without failures.

        Returns:
            bool: If the project validation result was ok.
        """
        return self.status.value in (ValidationStatus.SUCCESS, ValidationStatus.WARNING)


class MetadockProject:
    """Core abstraction for representing a Metadock project. Tracks and statefully manages the templated_documents,
    content_schematics, and generated_documents directories.

    Attributes:
        directory (Path): Path to the root of the metadock project directory (.metadock/)

    Cached Properties:
        content_schematics_directory (Path): Path to the content_schematics directory for the project
        content_schematics (dict[str, MetadockContentSchematic]): Dictionary of content schematics, keyed by name
        generated_documents_directory (Path): Path to the generated_documents directory for the project
        templated_documents_directory (Path): Path to the templated_documents directory for the project
        templated_documents (dict[str, MetadockTemplatedDocument]): Dictionary of templated documents, keyed by project
            relative path.
    """

    directory: Path

    def __init__(self, directory: Path | str):
        """Open an existing Metadock project directory.

        Args:
            directory (Path | str): .metadock directory to open
        """
        self.directory = Path(directory)

    @cached_property
    def templated_documents_directory(self) -> Path:
        """Path to the templated_documents directory for the project."""
        return self.directory / "templated_documents"

    @cached_property
    def templated_documents(self) -> dict[str, "MetadockTemplatedDocument"]:
        """Returns a dictionary of templated documents, keyed by project relative path.

        Returns:
            dict[str, MetadockTemplatedDocument]: A dictionary containing MetadockTemplatedDocument objects,
            where the keys are the project relative paths of the documents.
        """
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
        """Path to the content_schematics directory for the project"""
        return self.directory / "content_schematics"

    @cached_property
    def content_schematics(self) -> dict[str, "MetadockContentSchematic"]:
        """Returns a dictionary of content schematics, keyed by name.

        This method collects content schematics from YAML files in the content schematics directory.
        Each content schematic is represented by a `MetadockContentSchematic` object.

        Returns:
            A dictionary of content schematics, where the keys are the names of the schematics and the values are the
            `MetadockContentSchematic` objects.
        """
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
        """Path to the generated_documents directory for the project"""
        return self.directory / "generated_documents"

    def build(self, schematics: Optional[list[str]] = None):
        """Build the compiled documents for the specified schematics.

        Args:
            schematics (Optional[list[str]]): List of schematic names to build. If None, build all schematics.
        """

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
        """Deletes all generated documents in the `generated_documents` project directory.

        This method removes all files and subdirectories within the `generated_documents_directory`
        and recreates the directory afterwards.
        """
        shutil.rmtree(self.generated_documents_directory)
        os.makedirs(self.generated_documents_directory)

    def validate(self) -> MetadockProjectValidationResult:
        """Validates the Metadock project by checking the existence of required directories.

        Returns:
            MetadockProjectValidationResult: The validation result containing any failures or warnings.
        """

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
        """Retrieves a list of schematics based on the provided glob patterns for schematic names and template names.

        Args:
            schematic_globs (list[str], optional): List of glob patterns for schematic names. Defaults to [].
            template_globs (list[str], optional): List of glob patterns for template names. Defaults to [].

        Returns:
            list[str]: A list of unique schematic names matching the provided glob patterns.
        """

        schematics: list[str] = []
        for schematic_glob in schematic_globs:
            schematics += self._query_schematics_by_name_glob(schematic_glob)
        for template_glob in template_globs:
            schematics += self._query_schematics_by_template_glob(template_glob)
        return list(set((schematics)))

    def _query_schematics_by_name_glob(self, schematic_glob: str) -> "list[str]":
        """Query the content schematics for the project by a glob pattern.

        Args:
            schematic_glob (str): The glob pattern to match against schematic names.

        Returns:
            list[str]: A list of schematic names that match the glob pattern.
        """
        return [
            schematic_name
            for schematic_name in self.content_schematics
            if fnmatch.fnmatch(schematic_name, schematic_glob)
        ]

    def _query_schematics_by_template_glob(self, template_glob: str) -> "list[str]":
        """Query the content schematics for the project by a glob pattern on the template paths they use.

        Args:
            template_glob (str): The glob pattern to match against template paths.

        Returns:
            list[str]: A list of schematic names whose template match the glob pattern.
        """
        return [
            schematic.name
            for schematic in self.content_schematics.values()
            if fnmatch.fnmatch(schematic.template, template_glob)
        ]


class MetadockTemplatedDocument(pydantic.BaseModel):
    """Core abstraction which represents a templated document in a Metadock project.

    Attributes:
        absolute_path (Path): The absolute path to the templated document.
        project_relative_path (Path): The path to the templated document relative to the .metadock/templated_documents
            project subdirectory.
    """

    absolute_path: Path
    project_relative_path: Path

    @classmethod
    def from_absolute_path(cls, absolute_path: Path | str):
        """Creates a `MetadockTemplatedDocument` instance from an absolute path to an existing template in the
        .metadock/templated_documents project subdirectory.

        Args:
            absolute_path (Path | str): The absolute path to the templated document.

        Raises:
            exceptions.MetadockProjectException: If the templated document is not in the Metadock project directory.

        Returns:
            MetadockTemplatedDocument: The created `MetadockTemplatedDocument` instance.
        """
        absolute_path = Path(absolute_path)

        if "/.metadock/templated_documents/" not in str(absolute_path):
            raise exceptions.MetadockProjectException("TemplatedDocument appears not to be in metadock project dir.")

        project_relative_path = Path(str(absolute_path).split("/.metadock/templated_documents/")[1])
        cls(absolute_path=absolute_path, project_relative_path=project_relative_path)

    @classmethod
    def from_project_relative_path(
        cls, project_dir: Path | str, project_relative_path: Path | str
    ) -> "MetadockTemplatedDocument":
        """Creates a `MetadockTemplatedDocument` instance from a path relative to the .metadock/templated_documents
        directory for this project

        Args:
            project_dir (Path | str): The path to the Metadock project directory.
            project_relative_path (Path | str): The path to the templated document relative to the
                .metadock/templated_documents project subdirectory.

        Returns:
            MetadockTemplatedDocument: The created `MetadockTemplatedDocument` instance.
        """
        project_relative_path = Path(project_relative_path)
        absolute_path = Path(project_dir) / "templated_documents" / Path(project_relative_path)
        return cls(absolute_path=absolute_path, project_relative_path=project_relative_path)

    def content(self) -> str:
        """Returns the raw content of the document template.

        Returns:
            str: The content of the templated document.
        """
        with self.absolute_path.open("r") as handle:
            return handle.read()

    def jinja_template(self) -> jinja2.Template:
        """Parses the content of the templated document as a Jinja2 template.

        Raises:
            exceptions.MetadockTemplateParsingException: If parsing the Jinja2 template fails.

        Returns:
            jinja2.Template: The parsed Jinja2 template.
        """
        try:
            return jinja2.Template(self.content())
        except Exception as e:
            raise exceptions.MetadockTemplateParsingException(
                "Failed to parse jinja2.Template from %s,\n\tdue to exception:\n%s"
                % (self.project_relative_path, str(e))
            )


class MetadockContentSchematic(pydantic.BaseModel):
    """Represents a content schematic in Metadock.

    Attributes:
        name (str): The unique name for the content schematic.
        template (str): The template to be used for rendering the content.
        target_formats (list[str]): The list of target formats for the compiled content.
        context (Any, optional): The context data to be used during rendering. Defaults to an empty dictionary.
    """

    name: str
    template: str
    target_formats: list[str]
    context: Any = {}

    def to_compiled_targets(self, project: MetadockProject) -> dict[str, str | bytes]:
        """
        Converts the content schematic to compiled targets based in the provided project.

        Args:
            project (MetadockProject): The Metadock project containing the templated documents.

        Returns:
            dict[str, str | bytes]: A dictionary mapping target format identifiers to the compiled content.
        """

        compiled_targets: dict[str, str | bytes] = {}

        for target_format in self.target_formats:
            target_format = MetadockTargetFormatFactory.target_format(target_format)
            templated_document = project.templated_documents[self.template]
            rendered_document = templated_document.jinja_template().render(self.context | MetadockEnv().dict())
            post_processed_document = target_format.handler(rendered_document)

            compiled_targets[target_format.identifier] = post_processed_document

        return compiled_targets

    @classmethod
    def collect_from_file(cls, yaml_path: Path | str) -> "list[MetadockContentSchematic]":
        """
        Collects content schematics from a YAML file. Flattens any merge keys in the YAML specification.

        Args:
            yaml_path (Path | str): The path to the YAML file.

        Returns:
            list[MetadockContentSchematic]: A list of content schematics parsed from the YAML file.

        Raises:
            MetadockContentSchematicParsingException: If the YAML file is not found or if a required key is missing.
        """

        yaml_path = Path(yaml_path)
        content_schematics: list[MetadockContentSchematic] = []

        if not yaml_path.exists():
            raise exceptions.MetadockContentSchematicParsingException(
                "Could not find content schematic file %s" % yaml_path
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
                    context=yaml_utils.flatten_merge_keys(def_schematic.get("context", {})),
                )
            )

        return content_schematics
