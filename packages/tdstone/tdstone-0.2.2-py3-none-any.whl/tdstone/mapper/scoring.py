def create_mapper_scoring(mapper_scoring):
    # sql query that creates the sto mapper table for model scoring
    sql_create_table = f"""
        CREATE MULTISET TABLE {mapper_scoring},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID BIGINT,
            ID_TRAINED_MODEL VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
            ID_PARTITION VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            STATUS VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            METADATA JSON(32000), 
            ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME	
        )
        PRIMARY INDEX (ID_TRAINED_MODEL);
    """

    return sql_create_table


def create_mapper_scoring_description(mapper_training_description):
    # sql query that creates the sto mapper description table for model scoring
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
            TRAINED_MODEL_REPO VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            METADATA JSON(32000)
        )
        PRIMARY INDEX (ID);
    """

    return sql_create_table