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