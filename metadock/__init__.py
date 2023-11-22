import os
from pathlib import Path
from typing import Optional, Self
from metadock import exceptions
from metadock.engine import MetadockProject, MetadockProjectValidationResult, MetadockContentSchematic


class Metadock:
    working_directory: Path
    metadock_directory: Path
    project: MetadockProject

    @classmethod
    def init(cls, working_directory: Path | str = Path.cwd()) -> Self:
        working_directory = Path(working_directory)
        metadock_directory = working_directory / ".metadock"

        if not working_directory.exists():
            os.makedirs(working_directory)

        if metadock_directory.exists():
            raise exceptions.MetadockProjectException("Project already exists in %s. Aborting." % working_directory)

        os.makedirs(metadock_directory)
        os.makedirs(metadock_directory / "content_schematics")
        os.makedirs(metadock_directory / "generated_documents")
        os.makedirs(metadock_directory / "templated_documents")

        return cls(working_directory)

    def __init__(self, working_directory: Path | str = Path.cwd()):
        """Instantiate a new Metadock instance in `working_directory`, or the current working directory. Expects there
        to exist a `.metadock` directory in `working_directory.`

        Args:
            working_directory (Path | str, optional): Location to parse metadock project. Defaults to Path.cwd().
        """
        working_directory = Path(working_directory)
        metadock_directory = working_directory / ".metadock"
        if not metadock_directory.exists() or not metadock_directory.is_dir():
            raise exceptions.MetadockProjectException(
                "Missing .metadock directory in working dir: %s" % working_directory
            )
        self.working_directory = working_directory
        self.metadock_directory = metadock_directory

        self.project = MetadockProject(self.metadock_directory)

    def validate(self) -> MetadockProjectValidationResult:
        return self.project.validate()

    def clean(self):
        return self.project.clean()

    def build(self, schematic_globs: list[str] = [], template_globs: list[str] = []):
        self.project.build(self.list(schematic_globs, template_globs))

    def list(self, schematic_globs: list[str] = [], template_globs: list[str] = []) -> list[str]:
        if schematic_globs or template_globs:
            return self.project.list(schematic_globs, template_globs)
        return list(self.project.content_schematics.keys())
