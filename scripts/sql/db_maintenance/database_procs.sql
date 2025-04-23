CREATE OR REPLACE PROCEDURE delete_execution_data(p_execution_tag VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_deleted_count INT;
BEGIN
    
    -- Exemplo de chamada:
    -- CALL delete_execution_data('wetag_xxxxxxxxxxxxx');
    
    -- Deletar da tabela execution_file
    DELETE FROM execution_file
    WHERE
        se_id IN (
            SELECT se_id
            FROM
                service_execution se
                JOIN workflow_execution we ON se.we_id = we.we_id
            WHERE
                execution_tag = p_execution_tag
        );
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from execution_file', v_deleted_count;

    -- Deletar da tabela execution_statistics
    DELETE FROM execution_statistics
    WHERE
        se_id IN (
            SELECT se_id
            FROM
                service_execution se
                JOIN workflow_execution we ON se.we_id = we.we_id
            WHERE
                execution_tag = p_execution_tag
        );
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from execution_statistics', v_deleted_count;

    -- Deletar da tabela service_execution
    DELETE FROM service_execution
    WHERE
        se_id IN (
            SELECT se_id
            FROM
                service_execution se
                JOIN workflow_execution we ON se.we_id = we.we_id
            WHERE
                execution_tag = p_execution_tag
        );
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from service_execution', v_deleted_count;

    -- Deletar da tabela workflow_execution
    DELETE FROM workflow_execution
    WHERE
        execution_tag = p_execution_tag;
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % rows from workflow_execution', v_deleted_count;
END;
$$;

-- Chamando a procedure com CALL
CALL delete_execution_data('wetag_xxxxxxxxxxxxx');
