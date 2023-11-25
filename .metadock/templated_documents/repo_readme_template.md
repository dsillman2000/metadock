# metadock

Templated documentation engine, powered by {{ links.get("Jinja2") }} + {{ links.get("marko") }}.

## Quick Intro

Using markdown (.md) as a common source format for rich text content, `metadock` allows you to define Jinja *templated
documents*  for various markdown docs that you'd like to format into a rich text document, e.g. Jira, Confluence, Agile,
Gitlab, or a static website. You can then compile your markdown documents using context variables supplied via yaml
*content schematics*.

A simple Metadock-enabled project might look something like this:

{{ md.codeblock(example_project.get("structure")) }}

The root of your project is expected to have a `.metadock` folder, which can be generated from the CLI using
`metadock init`.

## Basic CLI Usage

The `metadock` CLI, installed using `pip install metadock`, has {{ cli.get("commands") | length }} basic commands, 
spelled out in the help message:

{{ md.codeblock(cli.get("usage_string"), language="sh") }}

Each of the commands supports a programmatic invocation from the `metadock.Metadock` class via a Python interface.

{% for command, spec in cli.get("commands").items() -%}
{%- set command_details -%}
- **Description**: {{ spec.get("description") }}
- **Usage**: {{ md.code(spec.get("usage")) }}
- **Python interface**: 
    {%- set python_interface = spec.get("python_interface") %}
  - Name: {{ md.code(python_interface.get("method_name")) }}
  - Signature: {{ md.code(python_interface.get("signature")) }}
{%- endset -%}
{{ html.details(html.summary(html.code("metadock " ~ command)), (command_details | md.convert)) }}
{% endfor %}

## Example Usage

In the example above, we can imagine the content of our template, `gitlab_mr_template.md`, to look something like this:

{{
    md.codeblock(
        example_project.get("templated_documents").get("gitlab_mr_template.md"),
        language="md",
    )
}}

This is a very simple MR format which can easily be generalized to allow for quickly generating large sets of docs which
meet the same format and style requirements. An example *content schematic* which could service this template could
be in `gitlab_mr__feature1.yml`:
{{
    md.codeblock(
        example_project.get("content_schematics").get("gitlab_mr__feature1.yml"),
        language="yml",
    )
}}

By invoking the CLI with `metadock build`, our template is compiled to look something like this, in a markdown file
called `generated_documents/gitlab_mr__feature1.md`:

{{ md.blockquote(example_project.get("generated_documents").get("gitlab_mr__feature1.md")) }}

Because the `target_formats` we chose included `md+html` _and_ `md`, we also get an HTML rendering of the document for 
free, located at `generated_documents/gitlab_mr__feature_1.html`:

{{
    md.codeblock(
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
{{ md.list(md.code(target_format) ~ ":", md.list(data.get("description"))) }}
{% endfor -%}
- Anything else, e.g. `txt`, `sql` or `py`:
  - Generates the given template as plaintext, and adds the given string as a file extension, e.g. 
  `.txt`, `.sql` or `.py`.

## Jinja Templating Helpers

In the Jinja templating context which is loaded for each templated document, there are a handful of helpful Jinja macros
and filters which can be used to make formatting content easier. The macros and filters are segregated into 
{{ jinja_helpers.keys() | length }} namespaces, documented below:

{% for namespace, namespace_spec in jinja_helpers.items() -%}
{%- set namespace_title_prefix = "Global" if namespace == "global" else md.code(namespace) -%}
{%- set ns_code_prefix = (namespace ~ ".") if namespace != "global" else "" -%}
{%- set namespace_intro -%}
### {{ namespace_title_prefix }} namespace

{{ namespace_spec.get("info") }}
{% endset -%}
{%- set ns_macro_table -%}
{{ md.tablehead("Macro", "Signature", "Doc", bold=true) }}
{% for macro, macro_spec in namespace_spec.get("macros", {}).items() -%}
{{
    md.tablerow(
        html.code(ns_code_prefix ~ macro), 
        html.code(macro_spec.get("method_name") ~ ": " ~ macro_spec.get("signature")),
        (macro_spec.get("docstring") | inline | html.escape) ~ "<br/><br/>" ~ (md.codeblock(macro_spec.get("example"), language="py") 
        | md.convert | html.inline),
    )
}}
{% endfor -%}
{%- endset -%}
{%- set ns_filter_table -%}
{{ md.tablehead("Filter", "Signature", "Doc", bold=true) }}
{% for filter, filter_spec in namespace_spec.get("filters", {}).items() -%}
{{
    md.tablerow(
        html.code(ns_code_prefix ~ filter), 
        html.code(filter_spec.get("method_name") ~ ": " ~ filter_spec.get("signature")),
        (filter_spec.get("docstring") | inline | html.escape) ~ "<br/><br/>" ~ (md.codeblock(filter_spec.get("example"), language="py") 
        | md.convert | html.inline),
    )
}}
{% endfor -%}
{%- endset -%}
{{ namespace_intro }}

{{ html.details(html.summary("Jinja macro reference"), ns_macro_table) }}

{{ html.details(html.summary("Jinja filter reference"), ns_filter_table) }}

{% endfor %}

## Acknowledgements

Author{% if (authors | length) > 1 %}s{% endif %}:

{{ authors | md.list }}