INSERT INTO
  {schema_name}.{table_name}
SELECT
  {column_info}
FROM
  {schema_name}.temp_{table_name};
