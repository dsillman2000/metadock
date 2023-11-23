import pytest

from metadock.engine import MetadockProject


def test_env__debug(empty_metadock_project_dir, capture_prints):
    # Create a temporary directory for the Metadock project
    project_dir = empty_metadock_project_dir

    # Create some dummy files within the directories
    (project_dir / "templated_documents" / "template1.md").write_text("Document with no print statements.")
    (project_dir / "templated_documents" / "template2.md").write_text("Document. {{ debug('example') }}")

    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        content_schematics:
          - name: example1
            template: template1.md
            target_formats: [ md ]
          - name: example2
            template: template2.md
            target_formats: [ md ]
        """
    )

    metadock = MetadockProject(project_dir)
    metadock.build()

    stdout = "\n".join(map(str, capture_prints))
    assert stdout == "example"
