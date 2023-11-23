import pytest

from metadock import MetadockProject


@pytest.fixture
def metadock_project(empty_metadock_project_dir):
    # Create a temporary directory for the Metadock project
    project_dir = empty_metadock_project_dir

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
              var2: a test
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

    build_result = metadock_project.build()
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 4
    assert len(build_result.generated_documents) == 4
    assert all(gd.status == "new" for gd in build_result.generated_documents)

    metadock_project.clean()
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 0

    # Test building specific schematics
    build_result = metadock_project.build(["schematic1a"])
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 1
    assert len(build_result.generated_documents) == 1
    assert all(gd.status == "new" for gd in build_result.generated_documents)

    # Test re-build has "nochange" status
    build_result = metadock_project.build(["schematic1a"])
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 1
    assert len(build_result.generated_documents) == 1
    assert all(gd.status == "nochange" for gd in build_result.generated_documents)

    # Test re-build has "update" status
    (metadock_project.generated_documents_directory / "schematic1a.md").write_text("Different content.")
    build_result = metadock_project.build(["schematic1a"])
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 1
    assert len(build_result.generated_documents) == 1
    assert all(gd.status == "update" for gd in build_result.generated_documents)


def test_metadock_project_clean(metadock_project):
    metadock_project.clean()
    assert len(list(metadock_project.generated_documents_directory.glob("*"))) == 0


def test_metadock_project_validate(metadock_project):
    validation_result = metadock_project.validate()
    assert validation_result.ok


def test_metadock_project_list(metadock_project):
    schematics = metadock_project.list(schematic_globs=["schematic1*"])
    assert set(schematics) == {"schematic1a", "schematic1b"}


def test_metadock_templated_document(metadock_project):
    templated_doc_1 = metadock_project.templated_documents["template1.md"]
    templated_doc_2 = metadock_project.templated_documents["template2.md"]

    assert templated_doc_1.content() == "Simple plaintext document."
    assert templated_doc_2.content() == "{{ var1 }} is {{ var2 }}."


def test_metadock_content_schematic(metadock_project):
    content_schem_1a = metadock_project.content_schematics["schematic1a"]
    content_schem_1b = metadock_project.content_schematics["schematic1b"]
    content_schem_2a = metadock_project.content_schematics["schematic2a"]
    content_schem_2b = metadock_project.content_schematics["schematic2b"]

    assert content_schem_1a.template == "template1.md"
    assert content_schem_1b.template == "template1.md"
    assert content_schem_2a.template == "template2.md"
    assert content_schem_2b.template == "template2.md"

    assert content_schem_1a.target_formats == content_schem_1b.target_formats == ["md"]
    assert content_schem_2a.target_formats == content_schem_2b.target_formats == ["md"]

    assert content_schem_1a.context == content_schem_2a.context == {}
    assert content_schem_1b.context == {"var1": "This", "var2": "ignored"}
    assert content_schem_2b.context == {"var1": "This", "var2": "a test"}

    assert (
        content_schem_1a.to_compiled_targets(metadock_project)
        == content_schem_1b.to_compiled_targets(metadock_project)
        == {"md": "Simple plaintext document."}
    )

    assert content_schem_2a.to_compiled_targets(metadock_project) == {"md": " is ."}
    assert content_schem_2b.to_compiled_targets(metadock_project) == {"md": "This is a test."}
