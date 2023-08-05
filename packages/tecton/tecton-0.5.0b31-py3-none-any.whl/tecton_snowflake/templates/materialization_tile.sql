{%- set join_key_list = join_keys|join(", ")  %}
WITH _SOURCE_WITH_TILE_TIME AS (
    SELECT *,
        DATEADD('SECOND', -MOD(DATE_PART(EPOCH_SECOND, {{ timestamp_key }}), {{ slide_interval.ToSeconds() }}), DATE_TRUNC('SECOND', {{ timestamp_key }})) AS _TILE_TIMESTAMP_KEY
    FROM ({{ source }})
)
SELECT
    {{ join_key_list }},
    {%- for column, functions in aggregations.items() -%}
    {%- for prefix, snowflake_function in functions %}
    {%- if prefix == "SUM_OF_SQUARES" %}
    SUM(SQUARE({{ column }})) AS {{ prefix }}_{{ column }},
    {%- else %}
    {{ snowflake_function }}({{ column }}) AS {{ prefix }}_{{ column }},
    {%- endif %}
    {%- endfor %}
    {%- endfor %}
    _TILE_TIMESTAMP_KEY as {{ timestamp_key }}
FROM (
    _SOURCE_WITH_TILE_TIME
)
GROUP BY {{ join_key_list }}, _TILE_TIMESTAMP_KEY
