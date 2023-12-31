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

## Code splitting with YAML imports

In order to keep your content schematics DRY, you can use YAML imports to split your content schematics into multiple
YAML files. For example, if you have a set of content schematics responsible for laying out a "knowledge base" of 
services maintained by your team, you might have a YAML file for each service, e.g. 
`services/airflow/google_forms_scrubber.yml` and `services/pipelines/user_interaction_data_pipeline.yml` which 
separately model their respective service specifications.

A content schematic can import context from a specific YAML key in another YAML file by using the special _import-key_ 
object, e.g.:

{{
    md.codeblock(
        example_project.get("content_schematics").get("import_key_examples.yml"),
        language="yml",
    ) | md.convert
}}

Note that all paths for the `import` field are relative to the `content_schematics` folder for the project.
If you'd like to import the entire content of a file as context, you may omit the `key` field, e.g.:

{{
    md.codeblock(
        example_project.get("content_schematics").get("import_key_examples_2.yml"),
        language="yml",
    )
}}

At the moment, no protection against cyclic dependencies are implemented (apart from a recursion depth exception which
will likely be thrown before memory is consumed). Users are responsible for ensuring that their imports do not create
cyclic dependencies.

## Jinja Templating Helpers

In the Jinja templating context which is loaded for each templated document, there are a handful of helpful Jinja macros
and filters which can be used to make formatting content easier. The macros and filters are segregated into 
{{ jinja_helpers.keys() | length }} namespaces, documented below:

{% for namespace, namespace_spec in jinja_helpers.items() -%}
{%- set namespace_title_prefix = "Global" if namespace == "global" else md.code(namespace) -%}
{%- set ns_code_prefix = (namespace ~ ".") if namespace != "global" else "" -%}
{%- set namespace_intro -%}
### {{ namespace_title_prefix }} namespace

{{ namespace_spec.get("docstring") }}
{% endset -%}
{%- set ns_macro_intro -%}
{%- if namespace_spec.get("macros", {}).keys() | length %}
The following macros are available in the {{ namespace }} namespace:

{{ 
    namespace_spec.get("macros", {}).keys() 
    | map("with_prefix", ns_code_prefix) 
    | map("wrap", "`")
    | md.list
}}
{%- else -%}
There are no macros available in the {{ namespace }} namespace.
{%- endif -%}
{%- endset -%}
{%- set ns_macro_table -%}
{{ md.tablehead("Macro", "Signature", "Doc", bold=true) }}
{% for macro, macro_spec in namespace_spec.get("macros", {}).items() -%}
{{
    md.tablerow(
        html.pre(ns_code_prefix ~ macro), 
        html.pre(macro_spec.get("method_name") ~ ": " ~ macro_spec.get("signature")),
        (macro_spec.get("docstring") | inline | html.escape) ~ "<br/><br/>" ~ (html.pre(macro_spec.get("example")) 
        | html.inline),
    )
}}
{% endfor -%}
{%- endset -%}
{%- set ns_filter_intro -%}
{%- if namespace_spec.get("filters", {}).keys() | length %}
The following filters are available in the {{ namespace }} namespace:

{{ 
    namespace_spec.get("filters", {}).keys() 
    | map("with_prefix", ns_code_prefix) 
    | map("wrap", "`")
    | md.list
}}
{%- else -%}
There are no filters available in the {{ namespace }} namespace.
{%- endif -%}
{%- endset -%}
{%- set ns_filter_table -%}
{{ md.tablehead("Filter", "Signature", "Doc", bold=true) }}
{% for filter, filter_spec in namespace_spec.get("filters", {}).items() -%}
{{
    md.tablerow(
        html.pre(ns_code_prefix ~ filter), 
        html.pre(filter_spec.get("method_name") ~ ": " ~ filter_spec.get("signature")),
        (
            filter_spec.get("docstring") 
            | inline 
            | html.escape
        ) ~ "<br/><br/>" ~ (
            html.pre(filter_spec.get("example")) 
            | html.inline
        ),
    )
}}
{% endfor -%}
{%- endset -%}
{{ namespace_intro }}

<br><br>

#### Jinja macros
{{ ns_macro_intro }}

{% if namespace_spec.get("macros", {}).keys() | length -%}
{{ html.details(html.summary(html.bold("Jinja macro reference")), ns_macro_table) }}
{%- endif %}

<br><br>

#### Jinja filters
{{ ns_filter_intro }}

{% if namespace_spec.get("filters", {}).keys() | length -%}
{{ html.details(html.summary(html.bold("Jinja filter reference")), ns_filter_table) }}
{% endif %}
<br><br>

---

{% endfor %}

## Acknowledgements

Author{% if (authors | length) > 1 %}s{% endif %}:

{{ authors | md.list }}