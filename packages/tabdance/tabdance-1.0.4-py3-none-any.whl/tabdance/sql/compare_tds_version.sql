SELECT
  file_name, table_name
FROM
  {schema_name}.{table_name}
WHERE
  file_name =  '{tds_file_name}'
  AND table_name = '{tds_table_name}'
  AND csv_hash <> '{tds_csv_hash}'
;
