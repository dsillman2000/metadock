import pytest

from metadock import MetadockProject


@pytest.fixture
def metadock_project(tmp_path):
    # Create a temporary directory for the Metadock project
    project_dir = tmp_path / ".metadock"
    project_dir.mkdir()

    # Create the necessary directories within the project
    (project_dir / "templated_documents").mkdir()
    (project_dir / "content_schematics").mkdir()
    (project_dir / "generated_documents").mkdir()

    # Create some dummy files within the directories
    (project_dir / "templated_documents" / "template1.md").write_text("Simple plaintext document.")
    (project_dir / "templated_documents" / "template2.md").write_text("{{ var1 }} is {{ var2 }}.")
    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        content_schematics:
                                                                       
          - name: schematic1a
            template: template1.md
            target_formats: [ md ]
            context: { }
                                                                       
          - name: schematic1b
            template: template1.md
            target_formats: [ md ]
            context:
              var1: This
              var2: ignored
        """
    )
    (project_dir / "content_schematics" / "schematic2.yml").write_text(
        """
        content_schematics:
                                                                       
          - name: schematic2a
            template: template2.md
            target_formats: [ md ]
            context: { }
                                                                       
          - name: schematic2b
            template: template2.md
            target_formats: [ md ]
            context:
              var1: This
              var2: ignored
        """
    )

    return MetadockProject(project_dir)


def test_metadock_project_templated_documents_directory(metadock_project):
    assert metadock_project.templated_documents_directory.name == "templated_documents"


def test_metadock_project_templated_documents(metadock_project):
    assert len(metadock_project.templated_documents) == 2


def test_metadock_project_content_schematics_directory(metadock_project):
    assert metadock_project.content_schematics_directory.name == "content_schematics"


def test_metadock_project_content_schematics(metadock_project):
    assert len(metadock_project.content_schematics) == 4


def test_metadock_project_generated_documents_directory(metadock_project):
    assert metadock_project.generated_documents_directory.name == "generated_documents"


def test_metadock_project_build(metadock_project):
    # Test building all schematics
    metadock_project.build()
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 4
    metadock_project.clean()
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 0

    # Test building specific schematics
    metadock_project.build(["schematic1a"])
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 1


def test_metadock_project_clean(metadock_project):
    metadock_project.clean()
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 0


def test_metadock_project_validate(metadock_project):
    validation_result = metadock_project.validate()
    assert validation_result.ok


def test_metadock_project_list(metadock_project):
    schematics = metadock_project.list(schematic_globs=["schematic1*"])
    assert set(schematics) == {"schematic1a", "schematic1b"}
