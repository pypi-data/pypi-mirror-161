SELECT
  table_name, file_name
FROM
  {schema_name}.{table_name}
WHERE
  file_name =  '{tds_file_name}'
;
