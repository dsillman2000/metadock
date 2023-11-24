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
        {{ md.tablehead("Name", "Contact", "Last contacted date", bold=table.get("bold_header")) }}
        {% for row in table["rows"] -%}
        {{ md.tablerow(row["name"], row["contact"], row["last_contact"]) }}
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
              table:
                # bold_header: false
                rows: *table_rows

          - name: example2
            template: template1.md
            target_formats: [ md ]
            context:
              table:
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

{{ md.blockquote(kirk_quote) }}"""
    )
    (project_dir / "templated_documents" / "template2.md").write_text(
        """As Captain Kirk once said,

{{ md.blockquote("This reminds me of something Spock said once: \n\n" ~ md.blockquote(spock_quote)) }}"""
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

{{ md.codeblock(code_text, language=language) }}"""
    )
    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        content_schematics:
          - name: example1
            template: template1.md
            target_formats: [ md ]
            context:
              code_text: "lambda u: u.upper()"

          - name: example2
            template: template1.md
            target_formats: [ md ]
            context:
              code_text: |
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


def test_env__code(empty_metadock_project_dir):
    project_dir = empty_metadock_project_dir
    (project_dir / "templated_documents" / "template1.md").write_text("""The password is {{ md.code("secret123") }}""")
    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        content_schematics:
          - name: example1
            template: template1.md
            target_formats: [ md ]

        """
    )

    metadock = MetadockProject(project_dir)
    metadock.build()

    assert (project_dir / "generated_documents" / "example1.md").read_text() == ("""The password is `secret123`""")


def test_env__list(empty_metadock_project_dir):
    project_dir = empty_metadock_project_dir
    (project_dir / "templated_documents" / "simple.md").write_text(
        """The list of fruit names is:

{{ md.list(fruits.keys()) }}

Their prices are:

{{ md.list(fruits.values()) }}"""
    )
    (project_dir / "templated_documents" / "simple_2.md").write_text(
        """The list of fruit names is:

{{ fruits.keys() | md.list }}

Their prices are:

{{ fruits.values() | md.list }}"""
    )
    (project_dir / "templated_documents" / "complex.md").write_text(
        """
{%- set fruit_price_lists =  fruits.values() | map("with_prefix", "Price: $") | map("md.list") -%}
{%- set fruit_prices = fruits.keys() | zip(fruit_price_lists) | chain | md.list -%}
The list of fruits is:

{{ fruit_prices }}"""
    )
    (project_dir / "content_schematics" / "schematic1.yml").write_text(
        """
        fruit_data: &fruit_data
          apple: 3.95
          banana: 1.00
          cherry: 0.20

        content_schematics:
          - name: example1
            template: simple.md
            target_formats: [ md ]
            context:
              fruits: *fruit_data

          - name: example1_2
            template: simple_2.md
            target_formats: [ md ]
            context:
              fruits: *fruit_data

          - name: example2
            template: complex.md
            target_formats: [ md ]
            context:
              fruits: *fruit_data
        """
    )

    metadock = MetadockProject(project_dir)
    metadock.build()

    assert (
        (project_dir / "generated_documents" / "example1.md").read_text()
        == (project_dir / "generated_documents" / "example1_2.md").read_text()
        == (
            """The list of fruit names is:

- apple
- banana
- cherry

Their prices are:

- 3.95
- 1.00
- 0.20"""
        )
    )
    assert (project_dir / "generated_documents" / "example2.md").read_text() == (
        """The list of fruits is:

- apple
  - Price: $3.95
- banana
  - Price: $1.00
- cherry
  - Price: $0.20"""
    )
