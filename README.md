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

The `metadock` CLI, installed using `pip install metadock`, has five basic commands, spelled out in the help message:

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
#... 
# yaml anchor definitions 
#...

content_schematics:

- name: gitlab_mr__feature1
  template: gitlab_mr_template.md
  target_formats: [ md+html, md ]

  context:

    jira:
      <<: *JiraProject-IGDP
      ticket_num: "13"

    merge_request:
      summary: Adding software version as hard requirement for staging
      changes:
        - "Added software version to staging model."
        - "Added unit tests for valid software version, invalid software version, missing software version."
      breaking_changes:
        - summary: "Dropping all records which are missing software version."
          affected_downstream: 
            - *Stakeholder-Service
            - *Stakeholder-Analytics
          suggested_remedy: |
            - Drop all records which are missing software version.
            - Add software version as a hard requirement for staging.
```

Which will get compiled to look something like this, in a markdown file called 
`generated_documents/gitlab_mr__feature1.md`:

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

Because the `target_formats` we chose included `md+html` _and_ `md`, we also get an HTML rendering of the document for free, 
located at `generated_documents/gitlab_mr__feature_1.html`:

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
- Anything else, e.g. `txt`, `sql` or `py`
  - Generates the given template as plaintext, and adds the given string as a file extension, e.g. `.txt`, `.sql` or 
    `.py`.

## Acknowledgements

Author:

- David Sillman <dsillman2000@gmail.com>