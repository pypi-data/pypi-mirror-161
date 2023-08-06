{% from 'copier_macro.sql' import copy_into %}

{#
  This template uses Snowflake scripting features and needs to be run inside e.g. EXECUTE IMMEDIATE. The EXECUTE
  IMMEDIATE itself is not in the template so we can format the SQL before putting the whole thing into a string.

  At a high level, the script does an insert of the source query into destination_table, with an additional
  materialization ID column set to the constant materialization_id value. It then unloads all rows with the
  matching materialization_id (to ignore previously written data) into destination_stage.
#}

{# This starts a Snowflake scripting block and is unrelated to BEGIN TRANSACTION #}
BEGIN

{# create objects required for offline materialization if they do not currently exist #}
CREATE SCHEMA IF NOT EXISTS {{ workspace }};
CREATE TABLE IF NOT EXISTS {{ destination_table }}(
    {%- for column in materialization_schema.columns %}
    {{ column.name }} {{ column.raw_snowflake_type}},
    {%- endfor %}
    __tecton_internal_materialization_id varchar
);
CREATE VIEW IF NOT EXISTS {{ destination_view }} AS (SELECT
    {%- for column in materialization_schema.columns %}
    {{ column.name }}{%- if not loop.last %}, {%- endif %}
    {%- endfor %}
FROM {{ destination_table }});

BEGIN TRANSACTION;

{# insert into the snowflake table #}
INSERT INTO {{ destination_table }}(
    {%- for column in materialization_schema.columns %}
    {{ column.name }},
    {%- endfor %}
    __tecton_internal_materialization_id
)
WITH SOURCE AS ( {{  source }} )
SELECT *, '{{ materialization_id }}' AS __tecton_internal_materialization_id
FROM SOURCE
;

{# copy inserted rows into the stage #}
{% set copy_source %}
SELECT *
FROM {{ destination_table }}
WHERE __tecton_internal_materialization_id = '{{ materialization_id }}'
{% endset %}
LET RES RESULTSET := (
    {{  copy_into(destination_stage, copy_source, materialization_schema, cast_types) }}
);
COMMIT;
RETURN TABLE(RES);

END;
