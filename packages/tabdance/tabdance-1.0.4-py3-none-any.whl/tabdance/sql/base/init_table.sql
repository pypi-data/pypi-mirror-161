CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
    file_name   varchar(255) UNIQUE NOT NULL,
    table_name  varchar(255) NOT NULL,
    csv_hash    text NOT NULL
);
