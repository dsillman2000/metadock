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

The global namespace contains helpful macros and filters for manipulating data in the Jinja
context. It also provides access to more specific namespaces through their respective identifiers,
such as `md` and `html`.



<details>
<summary>
Jinja macro reference
</summary>

| <b>Macro</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <code>debug</code> | <code>metadock.env.MetadockEnv.debug: (self, message: str) -> None</code> | Prints a debug message to stdout, and returns an empty string.<br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;No changes!{{ debug(&#x27;This is a debug message.&#x27;) }}&quot;).render()<br/>This is a debug message.<br/>&#x27;No changes!&#x27;<br/></code></pre><br/> |

</details>

<details>
<summary>
Jinja filter reference
</summary>

| <b>Filter</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <code>chain</code> | <code>metadock.env.MetadockEnv.chain_filter: (self, iterables: Sequence[Iterable[Any]]) -> Iterable[Any]</code> | Filter which flattens a sequence of iterables into a single iterable. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&#x27;{{ {&quot;first&quot;: 1, &quot;second&quot;: 2}.items() \| chain \| join(&quot; &quot;) }}&#x27;).render()<br/>&#x27;first 1 second 2&#x27;<br/></code></pre><br/> |
| <code>inline</code> | <code>metadock.env.MetadockEnv.inline_filter: (self, value: str) -> str</code> | Filter which inlines a string by replacing all newlines with spaces, and all double spaces with single spaces. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ &#x27;This is a multi-line string.\nThis is the second line.\nAnd the third.&#x27; \| inline }}&quot;).render()<br/>&#x27;This is a multi-line string. This is the second line. And the third.&#x27;<br/></code></pre><br/> |
| <code>with_prefix</code> | <code>metadock.env.MetadockEnv.with_prefix_filter: (self, value: str, prefix: str, sep: str = '') -> str</code> | Filter which prepends a prefix to a string, with an optional separator. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ &#x27;This is a string.&#x27; \| with_prefix(&#x27;Prefix&#x27;) }}&quot;).render()<br/>&#x27;PrefixThis is a string.&#x27;<br/>&gt;&gt;&gt; env.from_string(&quot;{{ &#x27;This is a string.&#x27; \| with_prefix(&#x27;Prefix: &#x27;, sep = &#x27; : &#x27;) }}&quot;).render()<br/>&#x27;Prefix : This is a string.&#x27;<br/></code></pre><br/> |
| <code>with_suffix</code> | <code>metadock.env.MetadockEnv.with_suffix_filter: (self, value: str, suffix: str, sep: str = '') -> str</code> | Filter which appends a suffix to a string, with an optional separator. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ &#x27;This is a string&#x27; \| with_suffix(&#x27;Suffix&#x27;) }}&quot;).render()<br/>&#x27;This is a stringSuffix&#x27;<br/>&gt;&gt;&gt; env.from_string(&quot;{{ &#x27;This is a string&#x27; \| with_suffix(&#x27;Suffix&#x27;, sep = &#x27; : &#x27;) }}&quot;).render()<br/>&#x27;This is a string : Suffix&#x27;<br/></code></pre><br/> |
| <code>zip</code> | <code>metadock.env.MetadockEnv.zip_filter: (self, input_iterable: Iterable[Any], *iterables: Iterable[Any]) -> Iterable[tuple[Any, ...]]</code> | Filter which zips an input iterable with one or more iterables. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ [&#x27;a&#x27;, &#x27;b&#x27;, &#x27;c&#x27;] \| zip([1, 2, 3]) \| list }}&quot;).render()<br/>&quot;[(&#x27;a&#x27;, 1), (&#x27;b&#x27;, 2), (&#x27;c&#x27;, 3)]&quot;<br/></code></pre><br/> |

</details>

### `md` namespace

None


<details>
<summary>
Jinja macro reference
</summary>

| <b>Macro</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |

</details>

<details>
<summary>
Jinja filter reference
</summary>

| <b>Filter</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |

</details>

### `html` namespace

None


<details>
<summary>
Jinja macro reference
</summary>

| <b>Macro</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |
| <code>html.bold</code> | <code>metadock.env.MetadockHtmlNamespace.bold: (self, content: str) -> str</code> | Wraps a string in HTML bold tags (&lt;b&gt;&lt;/b&gt;). <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ html.bold(&#x27;This is bold text.&#x27;) }}&quot;).render()<br/>&#x27;&lt;b&gt;This is bold text.&lt;/b&gt;&#x27;<br/></code></pre><br/> |
| <code>html.code</code> | <code>metadock.env.MetadockHtmlNamespace.code: (self, content: str) -> str</code> | Wraps a string in HTML code tags (&lt;code&gt;&lt;/code&gt;). <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ html.code(&#x27;This is code text.&#x27;) }}&quot;).render()<br/>&#x27;&lt;code&gt;This is code text.&lt;/code&gt;&#x27;<br/></code></pre><br/> |
| <code>html.codeblock</code> | <code>metadock.env.MetadockHtmlNamespace.codeblock: (self, content: str, indent: int = 0) -> str</code> | Wraps a string in preformatted HTML code tags (&lt;pre&gt;&lt;code&gt;&lt;/code&gt;&lt;/pre&gt;), and indents the content by the given amount. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ html.codeblock(&#x27;This is code text.&#x27;, indent = 4) }}&quot;).render()<br/>&#x27;&lt;pre&gt;&lt;code&gt;    This is code text.&lt;/code&gt;&lt;/pre&gt;&#x27;<br/></code></pre><br/> |
| <code>html.details</code> | <code>metadock.env.MetadockHtmlNamespace.details: (self, *contents: str) -> str</code> | Wraps a string in line-broken HTML details tags (&lt;details&gt;&lt;/details&gt;). Multiple arguments get separated by two line breaks. <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ html.details(&#x27;This is details text.&#x27;) }}&quot;).render()<br/>&#x27;&lt;details&gt;\nThis is details text.\n&lt;/details&gt;&#x27;<br/></code></pre><br/> |
| <code>html.italic</code> | <code>metadock.env.MetadockHtmlNamespace.italic: (self, content: str) -> str</code> | Wraps a string in HTML italic tags (&lt;i&gt;&lt;/i&gt;). <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ html.italic(&#x27;This is italic text.&#x27;) }}&quot;).render()<br/>&#x27;&lt;i&gt;This is italic text.&lt;/i&gt;&#x27;<br/></code></pre><br/> |
| <code>html.summary</code> | <code>metadock.env.MetadockHtmlNamespace.summary: (self, content: str) -> str</code> | Wraps a string in line-broken HTML summary tags (&lt;summary&gt;\n\n&lt;/summary&gt;). <br/><br/><pre><code>&gt;&gt;&gt; from metadock.env import MetadockEnv<br/>&gt;&gt;&gt; env = MetadockEnv().jinja_environment()<br/>&gt;&gt;&gt; env.from_string(&quot;{{ html.summary(&#x27;This is summary text.&#x27;) }}&quot;).render()<br/>&#x27;&lt;summary&gt;\nThis is summary text.\n&lt;/summary&gt;&#x27;<br/></code></pre><br/> |

</details>

<details>
<summary>
Jinja filter reference
</summary>

| <b>Filter</b> | <b>Signature</b> | <b>Doc</b> |
| --- | --- | --- |

</details>



## Acknowledgements

Author:

- David Sillman <dsillman2000@gmail.com>