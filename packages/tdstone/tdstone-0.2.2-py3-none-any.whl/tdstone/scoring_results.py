def create_scoring_results(scoring_results_table_name, data_type=None):
    # sql query that creates the sto model repository table

    if data_type:
        table_name = f'{scoring_results_table_name}_{data_type.split("(")[0]}'
        feature_type = ''
    else:
        table_name = f'{scoring_results_table_name}'
        data_type = 'VARCHAR(255)'
        feature_type = 'FEATURE_TYPE VARCHAR(20) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,'

    sql_create_table = f"""
        CREATE MULTISET TABLE {table_name},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID_PARTITION VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            ID_ROW VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            FEATURE_NAME VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            FEATURE_VALUE {data_type},
            {feature_type}
            --STATUS VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC ,
            ID_PROCESS BIGINT,
            ID_MODEL BIGINT,
            MODEL_TYPE VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            ID_TRAINED_MODEL VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            insertTImestamp TIMESTAMP(6) WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP(6)
            --ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            --ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            --PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME	

        )
        --PRIMARY INDEX (ID_ROW, FEATURE_NAME);
        NO PRIMARY INDEX
    """

    return sql_create_table