-- Use the schema set in dbt_project.yml as is (staging, marts), not prefixed with the target schema.
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name or target.schema }}
{%- endmacro %}
