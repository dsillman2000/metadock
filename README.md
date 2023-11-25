# metadock

Templated documentation engine, powered by [Jinja2](https://github.com/pallets/jinja) + [marko](https://github.com/frostming/marko).

## Quick Intro

Using markdown (.md) as a common source format for rich text content, `metadock` allows you to define Jinja *templated
documents*  for various markdown docs that you'd like to format into a rich text document, e.g. Jira, Confluence, Agile,
Gitlab, or a static website. You can then compile your markdown documents using context variables supplied via yaml
*content schematics*.

A simple Metadock-enabled project might look something like this:

```
MyProject/
  - ...
  - <my project content>
  - ...
  - .metadock/
      - templated_documents/
          - gitlab_mr_template.md
      - content_schematics/
          - gitlab_mr__feature1.yml
          - gitlab_mr__otherfeature.yml
      - generated_documents/
          - gitlab_mr__feature1.md
          - gitlab_mr__feature1.html
          - gitlab_mr__otherfeature.md
          - gitlab_mr__otherfeature.html
```

The root of your project is expected to have a `.metadock` folder, which can be generated from the CLI using
`metadock init`.

## Basic CLI Usage

The `metadock` CLI, installed using `pip install metadock`, has 5 basic commands, 
spelled out in the help message:

```sh
usage: metadock [-h] [-p PROJECT_DIR] {init,validate,build,list,clean} ...

Generates and formats Jinja documentation templates from yaml sources.

positional arguments:
  {init,validate,build,list,clean}
                        Metadock command
    init                Initialize a new Metadock project in a folder which does not currently have one.
    validate            Validate the structure of an existing Metadock project.
    build               Build a Metadock project, rendering some or all documents.
    list                List all recognized documents which can be generated from a given selection.
    clean               Cleans the generated_documents directory for the Metadock project.

options:
  -h, --help            show this help message and exit
  -p PROJECT_DIR, --project-dir PROJECT_DIR
                        Project directory containing a .metadock directory.
```

Each of the commands supports a programmatic invocation from the `metadock.Metadock` class via a Python interface.

<details>
<summary>
<code>metadock init</code>
</summary>

<ul>
<li><strong>Description</strong>: Used to initialize a fresh Metadock project in a folder which does not currently have one.</li>
<li><strong>Usage</strong>: <code>metadock [-p PROJECT_DIR] init</code></li>
<li>
<strong>Python interface</strong>:<ul>
<li>Name: <code>metadock.Metadock.init</code></li>
<li>Signature: <code>(self, working_directory: Path | str = Path.cwd()) -&gt; metadock.Metadock</code></li>
</ul>
</li>
</ul>

</details>
<details>
<summary>
<code>metadock validate</code>
</summary>

<ul>
<li><strong>Description</strong>: Used to validate the structure of an existing Metadock project.</li>
<li><strong>Usage</strong>: <code>metadock [-p PROJECT_DIR] validate</code></li>
<li>
<strong>Python interface</strong>:<ul>
<li>Name: <code>metadock.Metadock.validate</code></li>
<li>Signature: <code>(self) -&gt; metadock.engine.MetadockProjectValidationResult</code></li>
</ul>
</li>
</ul>

</details>
<details>
<summary>
<code>metadock build</code>
</summary>

<ul>
<li><strong>Description</strong>: Used to build a Metadock project, rendering some or all documents.</li>
<li><strong>Usage</strong>: <code>metadock [-p PROJECT_DIR] build [-s SCHEMATIC_GLOBS [SCHEMATIC_GLOBS ...]] [-t TEMPLATE_GLOBS [TEMPLATE_GLOBS ...]]</code></li>
<li>
<strong>Python interface</strong>:<ul>
<li>Name: <code>metadock.Metadock.build</code></li>
<li>Signature: <code>&quot;(self, schematic_globs: list[str] = [], template_globs: list[str] = []) -&gt;  metadock.engine.MetadockProjectBuildResult&quot;</code></li>
</ul>
</li>
</ul>

</details>
<details>
<summary>
<code>metadock list</code>
</summary>

<ul>
<li><strong>Description</strong>: Used to list all recognized documents which can be generated from a given selection.</li>
<li><strong>Usage</strong>: <code>metadock [-p PROJECT_DIR] list [-s SCHEMATIC_GLOBS [SCHEMATIC_GLOBS ...]] [-t TEMPLATE_GLOBS [TEMPLATE_GLOBS ...]]</code></li>
<li>
<strong>Python interface</strong>:<ul>
<li>Name: <code>metadock.Metadock.list</code></li>
<li>Signature: <code>(self, schematic_globs: list[str] = [], template_globs: list[str] = []) -&gt;  list[str]</code></li>
</ul>
</li>
</ul>

</details>
<details>
<summary>
<code>metadock clean</code>
</summary>

<ul>
<li><strong>Description</strong>: Used to clean the generated_documents directory for the Metadock project.</li>
<li><strong>Usage</strong>: <code>metadock [-p PROJECT_DIR] clean</code></li>
<li>
<strong>Python interface</strong>:<ul>
<li>Name: <code>metadock.Metadock.clean</code></li>
<li>Signature: <code>(self) -&gt; None</code></li>
</ul>
</li>
</ul>

</details>


## Example Usage

In the example above, we can imagine the content of our template, `gitlab_mr_template.md`, to look something like this:

```md
{%- set jira_project_name = jira.get('project_name') -%}
{%- set jira_project_id = jira.get('project_id') -%}
{%- set jira_ticket_num = jira.get('ticket_num') -%}
{%- set jira_ticket_id = jira_project_name ~ "-" ~ jira_ticket_num -%}
{%- set mr_summary = merge_request.get('summary') -%}
# [{{ jira_ticket_id }}] {{ mr_summary }}

Welcome to my MR. Some of the changes are listed below:

{% for change in merge_request.get('changes', []) -%}
{{ loop.index }}. {{ change }}{{ "\n" if not loop.last else "" }}
{%- endfor %}

{% if merge_request.get('breaking_changes') -%}
In addition to the changes above, there are also a few breaking changes introduced in this MR:

{% for breaking_change in merge_request.get('breaking_changes') -%}
- {{ breaking_change.get('summary') }}
  - **Affected downstream stakeholders**: {{ breaking_change.get('affected_downstream', [{'id': 'None'}]) | map(attribute='id') | join(", ") }}.
  - **Suggested remedy**: {{ breaking_change.get('suggested_remedy', 'None') }}{{ "\n" if not loop.last else "" }}
{%- endfor -%}
{%- endif %}

For more information, please check out the Jira ticket associated with this MR, {{ jira_ticket_id }}.
```

This is a very simple MR format which can easily be generalized to allow for quickly generating large sets of docs which
meet the same format and style requirements. An example *content schematic* which could service this template could
be in `gitlab_mr__feature1.yml`:
```yml
content_schematics:

- name: gitlab_mr__feature1
  template: gitlab_mr_template.md
  target_formats: [ md+html, md ]

  context:

    jira:
      project_name: "IGDP"
      project_id: "12001"
      ticket_num: "13"

    merge_request:
      summary: Adding software version as hard requirement for staging
      changes:
        - "Added software version to staging model."
        - "Added unit tests for valid software version, invalid software version, missing software version."
      breaking_changes:
        - summary: "Dropping all records which are missing software version."
          affected_downstream:
            - id: Service
              email: service@company.com
            - id: Analytics
              email: analytics-data@company.com
          suggested_remedy: |
            - Drop all records which are missing software version.
            - Add software version as a hard requirement for staging.
```

By invoking the CLI with `metadock build`, our template is compiled to look something like this, in a markdown file
called `generated_documents/gitlab_mr__feature1.md`:

> # [IGDP-13] Adding software version as hard requirement for staging
> 
> Welcome to my MR. Some of the changes are listed below:
> 
> 1. Added software version to staging model.
> 2. Added unit tests for valid software version, invalid software version, missing software version.
> 
> In addition to the changes above, there are also a few breaking changes introduced in this MR:
> 
> - Dropping all records which are missing software version.
>   - **Affected downstream stakeholders**: Service, Analytics.
>   - **Suggested remedy**:
>     - Drop all records which are missing software version.
>     - Add software version as a hard requirement for staging.
> 
> For more information, please check out the Jira ticket associated with this MR, IGDP-13.

Because the `target_formats` we chose included `md+html` _and_ `md`, we also get an HTML rendering of the document for 
free, located at `generated_documents/gitlab_mr__feature_1.html`:

```html
<h1>[IGDP-13] Adding software version as hard requirement for staging</h1>
<p>Welcome to my MR. Some of the changes are listed below:</p>
<ol>
<li>Added software version to staging model.</li>
<li>Added unit tests for valid software version, invalid software version, missing software version.</li>
</ol>
<p>In addition to the changes above, there are also a few breaking changes introduced in this MR:</p>
<ul>
<li>
Dropping all records which are missing software version.<ul>
<li><strong>Affected downstream stakeholders</strong>: Service, Analytics.</li>
<li><strong>Suggested remedy</strong>: Handle deletions manualy, using the software version column in the exposures to identify source records
which will be dropped, and drop them in the target environment after our change is deployed.</li>
</ul>
</li>
</ul>
<p>For more information, please check out the Jira ticket associated with this MR, IGDP-13.</p>
```

In a single *content schematics* yaml file, you can define any number of documents which should be generated (and to
what formats) using a given `template` and `context` (context variables loaded into the Jinja parser).

The `template` key should be a relative path to a Jinja template file from the `./metadock/templated_documents`
directory. The `name` key should be a unique identifier for the generated document, and will compose the basename of the
generated file.

The natively supported values for `target_formats` are:

- `md+html`:
  - Generates the given template, parses it into a markdown document, and then generates HTML from it.
- Anything else, e.g. `txt`, `sql` or `py`:
  - Generates the given template as plaintext, and adds the given string as a file extension, e.g. 
  `.txt`, `.sql` or `.py`.

## Jinja Templating Helpers

In the Jinja templating context which is loaded for each templated document, there are a handful of helpful Jinja macros
and filters which can be used to make formatting content easier. The macros and filters are segregated into 
3 namespaces, documented below:

### Global namespace

Jinja namespace for the global Metadock environment, including all global macros, filters, and namespaces.



#### Jinja macros

The following macros are available in the global namespace:

- `debug`

<details>
<summary>
<b>Jinja macro reference</b>
</summary>

| <b>Macro</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <pre>debug</pre> | <pre>metadock.env.MetadockEnv.debug: (self, message: str) -> None</pre> | Prints a debug message to stdout, and returns an empty string.<br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("No changes!{{ debug('This is a debug message.') }}").render()<br>This is a debug message.<br>'No changes!'<br></pre> |

</details>

#### Jinja filters

The following filters are available in the global namespace:

- `chain`
- `inline`
- `with_prefix`
- `with_suffix`
- `wrap`
- `zip`

<details>
<summary>
<b>Jinja filter reference</b>
</summary>

| <b>Filter</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <pre>chain</pre> | <pre>metadock.env.MetadockEnv.chain_filter: (self, iterables: Sequence[Iterable[Any]]) -> Iterable[Any]</pre> | Filter which flattens a sequence of iterables into a single iterable. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string('{{ {"first": 1, "second": 2}.items() \| chain \| join(" ") }}').render()<br>'first 1 second 2'<br></pre> |
| <pre>inline</pre> | <pre>metadock.env.MetadockEnv.inline_filter: (self, value: str) -> str</pre> | Filter which inlines a string by replacing all newlines with spaces, and all double spaces with single spaces. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ 'This is a multi-line string.\nThis is the second line.\nAnd the third.' \| inline }}").render()<br>'This is a multi-line string. This is the second line. And the third.'<br></pre> |
| <pre>with_prefix</pre> | <pre>metadock.env.MetadockEnv.with_prefix_filter: (self, value: str, prefix: str, sep: str = '') -> str</pre> | Filter which prepends a prefix to a string, with an optional separator. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ 'This is a string.' \| with_prefix('Prefix') }}").render()<br>'PrefixThis is a string.'<br>>>> env.from_string("{{ 'This is a string.' \| with_prefix('Prefix: ', sep = ' : ') }}").render()<br>'Prefix : This is a string.'<br></pre> |
| <pre>with_suffix</pre> | <pre>metadock.env.MetadockEnv.with_suffix_filter: (self, value: str, suffix: str, sep: str = '') -> str</pre> | Filter which appends a suffix to a string, with an optional separator. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ 'This is a string' \| with_suffix('Suffix') }}").render()<br>'This is a stringSuffix'<br>>>> env.from_string("{{ 'This is a string' \| with_suffix('Suffix', sep = ' : ') }}").render()<br>'This is a string : Suffix'<br></pre> |
| <pre>wrap</pre> | <pre>metadock.env.MetadockEnv.wrap_filter: (self, value: str, wrap: str) -> str</pre> | Filter which wraps an inner string with a given outer string. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> # Wrap with graves, like md.code(...)<br>>>> env.from_string("{{ 'This is a string.' \| wrap('`') }}").render()<br>'`This is a string.`'<br></pre> |
| <pre>zip</pre> | <pre>metadock.env.MetadockEnv.zip_filter: (self, input_iterable: Iterable[Any], *iterables: Iterable[Any]) -> Iterable[tuple[Any, ...]]</pre> | Filter which zips an input iterable with one or more iterables. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ ['a', 'b', 'c'] \| zip([1, 2, 3]) \| list }}").render()<br>"[('a', 1), ('b', 2), ('c', 3)]"<br></pre> |

</details>

### `md` namespace

Jinja Namespace for Markdown-related functions and filters.

**Macros**:

    blockquote
    code
    codeblock
    list
    tablehead
    tablerow

**Filters**:

    convert
    list



#### Jinja macros

The following macros are available in the md namespace:

- `md.blockquote`
- `md.code`
- `md.codeblock`
- `md.list`
- `md.tablehead`
- `md.tablerow`

<details>
<summary>
<b>Jinja macro reference</b>
</summary>

| <b>Macro</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <pre>md.blockquote</pre> | <pre>metadock.env.MetadockMdNamespace.blockquote: (self, content: str) -> str</pre> | Produces a Markdown blockquote from the given content by prepending each line with a gt symbol (&quot;&gt; &quot;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ md.blockquote('This is a blockquote.') }}").render()<br>'> This is a blockquote.'<br></pre> |
| <pre>md.code</pre> | <pre>metadock.env.MetadockMdNamespace.code: (self, content: str) -> str</pre> | Produces a Markdown inline code block from the given content by wrapping the string in graves (&quot;\`&quot;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ md.code('This is an inline code block.') }}").render()<br>'`This is an inline code block.`'<br></pre> |
| <pre>md.codeblock</pre> | <pre>metadock.env.MetadockMdNamespace.codeblock: (self, content: str, language: str = '') -> str</pre> | Produces a Markdown codeblock from the given content by wrapping the string in triple-graves (&quot;\`\`\`&quot;), and optionally specifies a language. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ md.codeblock('This is a codeblock.', language = 'sh') }}").render()<br>'```sh\nThis is a codeblock.\n```'<br></pre> |
| <pre>md.list</pre> | <pre>metadock.env.MetadockMdNamespace.list: (self, *items: str) -> str</pre> | Produces a Markdown list from the given content by prepending each line with a dash (&quot;- &quot;). If any of its arguments are, themselves, formatted as Markdown lists, then they are simply indented as sublists. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string(<br>...     "{{ md.list('This is a list.', md.list('This is a sublist,', 'in two pieces.')) }}"<br>... ).render()<br>'- This is a list.\n  - This is a sublist,\n  - in two pieces.'<br></pre> |
| <pre>md.tablehead</pre> | <pre>metadock.env.MetadockMdNamespace.tablehead: (self, *header_cells: str, bold: bool = False) -> str</pre> | Produces a Markdown table header from the given cells by joining each cell with pipes (&quot;\|&quot;) and wrapping the result in pipes, plus adding a header divider row. Cell contents have their pipes escaped with a backslash (&quot;\\&quot;). To bold the header cell contents, supply `bold = true`. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string(<br>...     "{{ md.tablehead('Column 1', 'Column 2', 'Column 3', bold = true) }}"<br>... ).render()<br>'\| <b>Column 1</b> \| <b>Column 2</b> \| <b>Column 3</b> \|\n\| --- \| --- \| --- \|'<br></pre> |
| <pre>md.tablerow</pre> | <pre>metadock.env.MetadockMdNamespace.tablerow: (self, *row_cells: str) -> str</pre> | Produces a Markdown table row from the given cells by joining each cell with pipes (&quot;\|&quot;) and wrapping the result in pipes. Cell contents have their pipes escaped with a backslash (&quot;\\&quot;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string(<br>...     "{{ md.tablehead('Column 1', 'Column 2', 'Column 3') }}\n"<br>...     "{{ md.tablerow('Value 1', 'Value 2', 'Value 3') }}"<br>... ).render()<br>'\| Column 1 \| Column 2 \| Column 3 \|\n\| --- \| --- \| --- \|\n\| Value 1 \| Value 2 \| Value 3 \|'<br></pre> |

</details>

#### Jinja filters

The following filters are available in the md namespace:

- `md.convert`
- `md.list`

<details>
<summary>
<b>Jinja filter reference</b>
</summary>

| <b>Filter</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <pre>md.convert</pre> | <pre>metadock.env.MetadockMdNamespace.convert_filter: (self, md_content: str) -> str</pre> | Filter which converts Markdown content to HTML, by invoking `marko.convert` (using github-flavored md). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ '# This is a heading\n\n> And a block quote.' \| md.convert }}").render()<br>'<h1>This is a heading</h1>\n<blockquote>\n<p>And a block quote.</p>\n</blockquote>\n'<br></pre> |
| <pre>md.list</pre> | <pre>metadock.env.MetadockMdNamespace.list_filter: (self, values: str \| Iterable[str]) -> str</pre> | Filter which unpacks an iterable of values into a Markdown list, or formats a single value as a Markdown list element. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string(<br>...     "{{ ['This is a list.', 'This is a second element'] \| md.list }}\n"<br>... ).render()<br>'- This is a list.\n- This is a second element\n'<br></pre> |

</details>

### `html` namespace

Jinja namespace which owns HTML-related functions and filters.



#### Jinja macros

The following macros are available in the html namespace:

- `html.bold`
- `html.code`
- `html.details`
- `html.italic`
- `html.pre`
- `html.summary`
- `html.underline`

<details>
<summary>
<b>Jinja macro reference</b>
</summary>

| <b>Macro</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <pre>html.bold</pre> | <pre>metadock.env.MetadockHtmlNamespace.bold: (self, content: str) -> str</pre> | Wraps a string in HTML bold tags (&lt;b&gt;&lt;/b&gt;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.bold('This is bold text.') }}").render()<br>'<b>This is bold text.</b>'<br></pre> |
| <pre>html.code</pre> | <pre>metadock.env.MetadockHtmlNamespace.code: (self, content: str) -> str</pre> | Wraps a string in HTML code tags (&lt;code&gt;&lt;/code&gt;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.code('This is code text.') }}").render()<br>'<code>This is code text.</code>'<br></pre> |
| <pre>html.details</pre> | <pre>metadock.env.MetadockHtmlNamespace.details: (self, *contents: str) -> str</pre> | Wraps a string in line-broken HTML details tags (&lt;details&gt;&lt;/details&gt;). Multiple arguments get separated by two line breaks. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.details('This is details text.') }}").render()<br>'<details>\nThis is details text.\n</details>'<br></pre> |
| <pre>html.italic</pre> | <pre>metadock.env.MetadockHtmlNamespace.italic: (self, content: str) -> str</pre> | Wraps a string in HTML italic tags (&lt;i&gt;&lt;/i&gt;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.italic('This is italic text.') }}").render()<br>'<i>This is italic text.</i>'<br></pre> |
| <pre>html.pre</pre> | <pre>metadock.env.MetadockHtmlNamespace.pre: (self, content: str, indent: int = 0) -> str</pre> | Wraps a string in preformatted HTML pre tags (&lt;pre&gt;&lt;/pre&gt;), and indents the content by the given amount. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.pre('This is code text.', indent = 4) }}").render()<br>'<pre>    This is code text.</pre>'<br></pre> |
| <pre>html.summary</pre> | <pre>metadock.env.MetadockHtmlNamespace.summary: (self, content: str) -> str</pre> | Wraps a string in line-broken HTML summary tags (&lt;summary&gt;\n\n&lt;/summary&gt;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.summary('This is summary text.') }}").render()<br>'<summary>\nThis is summary text.\n</summary>'<br></pre> |
| <pre>html.underline</pre> | <pre>metadock.env.MetadockHtmlNamespace.underline: (self, content: str) -> str</pre> | Wraps a string in HTML underline tags (&lt;u&gt;&lt;/u&gt;). <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ html.underline('This is underlined text.') }}").render()<br>'<u>This is underlined text.</u>'<br></pre> |

</details>

#### Jinja filters

The following filters are available in the html namespace:

- `html.escape`
- `html.inline`

<details>
<summary>
<b>Jinja filter reference</b>
</summary>

| <b>Filter</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <pre>html.escape</pre> | <pre>metadock.env.MetadockHtmlNamespace.escape_filter: (self, content: str) -> str</pre> | Filter which escapes a string by replacing all HTML special characters with their HTML entity equivalents. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ '<p>This is a paragraph.</p>' \| html.escape }}").render()<br>'&lt;p&gt;This is a paragraph.&lt;/p&gt;'<br></pre> |
| <pre>html.inline</pre> | <pre>metadock.env.MetadockHtmlNamespace.inline_filter: (self, content: str) -> str</pre> | Filter which inlines a string by replacing all newlines with HTML line-breaks &lt;br&gt; singleton tags. <br/><br/><pre>>>> from metadock.env import MetadockEnv<br>>>> env = MetadockEnv().jinja_environment()<br>>>> env.from_string("{{ 'This is a multi-line string.\nThis is the second line.\nAnd the third.' \| html.inline }}").render()<br>'This is a multi-line string.<br>This is the second line.<br>And the third.'<br></pre> |

</details>



## Acknowledgements

Author:

- David Sillman <dsillman2000@gmail.com>