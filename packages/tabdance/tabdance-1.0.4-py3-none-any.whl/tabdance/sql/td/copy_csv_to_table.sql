COPY
  {schema_name}.{table_name}
  FROM
    STDIN
  with
    (format csv, header true, delimiter ',')
