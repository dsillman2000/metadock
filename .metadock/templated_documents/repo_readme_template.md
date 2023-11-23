# metadock

Templated documentation engine, powered by {{ links.get("Jinja2") }} + {{ links.get("marko") }}.

## Quick Intro

Using markdown (.md) as a common source format for rich text content, `metadock` allows you to define Jinja *templated 
documents*  for various markdown docs that you'd like to format into a rich text document, e.g. Jira, Confluence, Agile, 
Gitlab, or a static website. You can then compile your markdown documents using context variables supplied via yaml 
*content schematics*.

A simple Metadock-enabled project might look something like this:

{{ codeblock(example_project.get("structure")) }}

The root of your project is expected to have a `.metadock` folder, which can be generated from the CLI using 
`metadock init`. 

## Basic CLI Usage

The `metadock` CLI, installed using `pip install metadock`, has five basic commands, spelled out in the help message:

{{ codeblock(cli.get("usage_string"), language="sh") }}

## Example Usage

In the example above, we can imagine the content of our template, `gitlab_mr_template.md`, to look something like this:

{{ 
    codeblock(
        example_project.get("templated_documents").get("gitlab_mr_template.md"),
        language="md",
    )
}}

This is a very simple MR format which can easily be generalized to allow for quickly generating large sets of docs which
meet the same format and style requirements. An example *content schematic* which could service this template could
be in `gitlab_mr__feature1.yml`:

{{ 
    codeblock(
        example_project.get("content_schematics").get("gitlab_mr__feature1.yml"),
        language="yml",
    )
}}

By invoking the CLI with `metadock build`, our template is compiled to look something like this, in a markdown file 
called `generated_documents/gitlab_mr__feature1.md`:

{{ blockquote(example_project.get("generated_documents").get("gitlab_mr__feature1.md")) }}

Because the `target_formats` we chose included `md+html` _and_ `md`, we also get an HTML rendering of the document for free, 
located at `generated_documents/gitlab_mr__feature_1.html`:

{{ 
    codeblock(
        example_project.get("generated_documents").get("gitlab_mr__feature1.html"),
        language="html",
    )
}}

In a single *content schematics* yaml file, you can define any number of documents which should be generated (and to 
what formats) using a given `template` and `context` (context variables loaded into the Jinja parser).

The `template` key should be a relative path to a Jinja template file from the `./metadock/templated_documents` 
directory. The `name` key should be a unique identifier for the generated document, and will compose the basename of the 
generated file. 

The natively supported values for `target_formats` are:
{% for target_format, data in target_formats.items() %}
{{ list(code(target_format) ~ ":", list(data.get("description"))) }}
{% endfor -%}
- Anything else, e.g. `txt`, `sql` or `py`
  - Generates the given template as plaintext, and adds the given string as a file extension, e.g. `.txt`, `.sql` or 
    `.py`.

## Acknowledgements

Author{% if (authors | length) > 1 %}s{% endif %}:

{{ list(*authors) }}