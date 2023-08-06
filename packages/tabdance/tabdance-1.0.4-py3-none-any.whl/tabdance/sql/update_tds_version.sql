UPDATE
  {schema_name}.{table_name}
SET
  csv_hash = '{tds_csv_hash}'
WHERE
  file_name = '{tds_file_name}'
  AND table_name = '{tds_table_name}'
  AND csv_hash <> '{tds_csv_hash}'
;
