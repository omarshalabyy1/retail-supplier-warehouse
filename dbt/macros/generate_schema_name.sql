-- Use the schema set in dbt_project.yml as is (silver, gold, semantic, analytical), not prefixed with the target schema.
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name or target.schema }}
{%- endmacro %}
