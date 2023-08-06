import teradataml as tdml

def create_trained_model_repository(trained_model_repository):
    # sql query that creates the sto model repository table
    sql_create_table = f"""
        CREATE MULTISET TABLE {trained_model_repository},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID_PROCESS BIGINT,
            ID_PARTITION VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            ID_MODEL BIGINT,
            ID_TRAINED_MODEL VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            MODEL_TYPE VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            STATUS VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            TRAINED_MODEL CLOB, 
            ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME	
        )
        PRIMARY INDEX (ID_PARTITION);
    """

    return sql_create_table


def create_code_model_trained_model_view(code_model_trained_model_view, code_model_view, trained_model_repository):
    # view that links the codes and the models

    sql_create_view = f"""
    REPLACE VIEW {code_model_trained_model_view} AS
    SEQUENCED VALIDTIME
    SELECT
        CODE_MODEL.ID_MODEL
    ,   CODE_MODEL.ID_CODE
    ,   TRAINED_MODEL.ID_PROCESS 
    ,   TRAINED_MODEL.ID_TRAINED_MODEL
    ,	CODE_MODEL.CODE_TYPE 
    ,	CODE_MODEL.CODE
    ,	CODE_MODEL.ARGUMENTS
    ,	CODE_MODEL.METADATA_MODEL
    ,	CODE_MODEL.METADATA_CODE
   
    ,   TRAINED_MODEL.ID_PARTITION
 
    ,   TRAINED_MODEL.MODEL_TYPE
    ,   TRAINED_MODEL.STATUS
    ,   TRAINED_MODEL.TRAINED_MODEL
    FROM
        {trained_model_repository} TRAINED_MODEL
    INNER JOIN	{code_model_view} CODE_MODEL
    ON TRAINED_MODEL.ID_MODEL = CODE_MODEL.ID_MODEL;
    """

    return sql_create_view


