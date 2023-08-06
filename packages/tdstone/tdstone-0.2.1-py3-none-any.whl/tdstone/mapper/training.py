def create_mapper_training(mapper_training):
    # sql query that creates the sto mapper table for model training
    sql_create_table = f"""
        CREATE MULTISET TABLE {mapper_training},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID BIGINT,
            ID_MODEL BIGINT,
            ID_PARTITION VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            STATUS VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            METADATA JSON(32000), 
            ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME	
        )
        PRIMARY INDEX (ID_MODEL);
    """

    return sql_create_table


def create_mapper_training_description(mapper_training_description):
    # sql query that creates the sto mapper description table for model training
    sql_create_table = f"""
        CREATE MULTISET TABLE {mapper_training_description},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID BIGINT,
            DATASET_OBJECT VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            COL_ID_ROW VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            COL_ID_PARTITION VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            COL_FOLD VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            METADATA JSON(32000)
        )
        PRIMARY INDEX (ID);
    """

    return sql_create_table