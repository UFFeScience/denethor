
--Copiar Tabelas
DO $$
DECLARE
    table_record RECORD;
    sequence_record RECORD;
    create_table_sql TEXT;
    insert_data_sql TEXT;
    create_sequence_sql TEXT;
    setval_sequence_sql TEXT;
BEGIN
    FOR table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        create_table_sql := format('CREATE TABLE backup_19_02_2025.%s (LIKE public.%s INCLUDING ALL);', table_record.tablename, table_record.tablename);
        RAISE NOTICE '%', create_table_sql;
        --EXECUTE create_table_sql;
        
        insert_data_sql := format('INSERT INTO backup_19_02_2025.%s SELECT * FROM public.%s;', table_record.tablename, table_record.tablename);
        RAISE NOTICE '%', insert_data_sql;
        --EXECUTE insert_data_sql;
    END LOOP;
END $$;

--Alterar Tabelas para remover dependência das sequences:
DO $$
DECLARE
    table_record RECORD;
    column_record RECORD;
    alter_column_sql TEXT;
BEGIN
    FOR table_record IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'backup_19_02_2025'
    LOOP
        FOR column_record IN
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'backup_19_02_2025' AND table_name = table_record.tablename AND column_default LIKE 'nextval%'
        LOOP
            alter_column_sql := format('ALTER TABLE backup_19_02_2025.%I ALTER COLUMN %I DROP DEFAULT', table_record.tablename, column_record.column_name);
            RAISE NOTICE '%', alter_column_sql;
            EXECUTE alter_column_sql;
        END LOOP;
    END LOOP;
END $$;





