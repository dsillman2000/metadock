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

    # Make sure "example" got printed out
    stdout = "\n".join(map(str, capture_prints))
    assert stdout == "example"

    # Make sure the debug statement left no artifact in the document
    assert (project_dir / "generated_documents" / "example1.md").read_text() == "Document with no print statements."
    assert (project_dir / "generated_documents" / "example2.md").read_text() == "Document. "


def test_env__table_helpers(empty_metadock_project_dir):
    # Create a temporary directory for the Metadock project
    project_dir = empty_metadock_project_dir

    # Create some dummy files within the directories
    (project_dir / "templated_documents" / "template1.md").write_text(
        """
        {{ table.header("Name", "Contact", "Last contacted date", bold=_table.get("bold_header")) }}
        {% for row in _table["rows"] -%}
        {{ table.row(row["name"], row["contact"], row["last_contact"]) }}
        {% endfor -%}
        """.strip().replace(
            "    ", ""
        )
    )

    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        .table_rows: &table_rows
          - name: John Doe
            contact: john.doe@company.com
            last_contact: 2021-01-01
          - name: Josh Doe
            contact: josh.doe@company.com
            last_contact: 2021-01-02

        content_schematics:
          - name: example1
            template: template1.md
            target_formats: [ md ]
            context:
              _table: 
                # bold_header: false
                rows: *table_rows

          - name: example2
            template: template1.md
            target_formats: [ md ]
            context:
              _table:
                bold_header: true
                rows: *table_rows
        """
    )

    metadock = MetadockProject(project_dir)
    metadock.build()

    # Make sure table without bold header got rendered
    assert (project_dir / "generated_documents" / "example1.md").read_text() == (
        "| Name | Contact | Last contacted date |\n"
        "| --- | --- | --- |\n"
        "| John Doe | john.doe@company.com | 2021-01-01 |\n"
        "| Josh Doe | josh.doe@company.com | 2021-01-02 |\n"
    )

    # Make sure table with bold header got rendered
    assert (project_dir / "generated_documents" / "example2.md").read_text() == (
        "| <b>Name</b> | <b>Contact</b> | <b>Last contacted date</b> |\n"
        "| --- | --- | --- |\n"
        "| John Doe | john.doe@company.com | 2021-01-01 |\n"
        "| Josh Doe | josh.doe@company.com | 2021-01-02 |\n"
    )


def test_env__blockquote(empty_metadock_project_dir):
    project_dir = empty_metadock_project_dir
    (project_dir / "templated_documents" / "template1.md").write_text(
        """As Captain Kirk once said,

{{ blockquote(kirk_quote) }}"""
    )
    (project_dir / "templated_documents" / "template2.md").write_text(
        """As Captain Kirk once said,

{{ blockquote("This reminds me of something Spock said once: \n\n" ~ blockquote(spock_quote)) }}"""
    )
    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        content_schematics:
          - name: example1
            template: template1.md
            target_formats: [ md ]
            context:
              kirk_quote: "Beam me up, Scotty!"
          - name: example2
            template: template2.md
            target_formats: [ md ]
            context:
              spock_quote: "Fascinating."
        """
    )

    metadock = MetadockProject(project_dir)
    metadock.build()

    assert (project_dir / "generated_documents" / "example1.md").read_text() == (
        """As Captain Kirk once said,

> Beam me up, Scotty!"""
    )
    assert (project_dir / "generated_documents" / "example2.md").read_text() == (
        """As Captain Kirk once said,

> This reminds me of something Spock said once: 
> 
> > Fascinating."""
    )


def test_env__codeblock(empty_metadock_project_dir):
    project_dir = empty_metadock_project_dir
    (project_dir / "templated_documents" / "template1.md").write_text(
        """The source code for this project:

{{ codeblock(code, language=language) }}"""
    )
    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        content_schematics:
          - name: example1
            template: template1.md
            target_formats: [ md ]
            context:
              code: "lambda u: u.upper()"

          - name: example2
            template: template1.md
            target_formats: [ md ]
            context:
              code: |
                def hello_world():
                    print("Hello, world!")
              language: py
        """
    )

    metadock = MetadockProject(project_dir)
    metadock.build()

    assert (project_dir / "generated_documents" / "example1.md").read_text() == (
        """The source code for this project:

```
lambda u: u.upper()
```"""
    )
    assert (project_dir / "generated_documents" / "example2.md").read_text() == (
        """The source code for this project:

```py
def hello_world():
    print("Hello, world!")
```"""
    )
