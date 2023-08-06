import teradataml as tdml


def create_model_repository(model_repository):
    # sql query that creates the sto model repository table
    sql_create_table = f"""
        CREATE MULTISET TABLE {model_repository},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID BIGINT,
            ID_CODE BIGINT,
            ARGUMENTS VARCHAR(32000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL, --JSON(32000),
            METADATA JSON(32000), 
            ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME	
        )
        PRIMARY INDEX (ID_CODE);
    """

    return sql_create_table


def create_code_model_view(code_model_view, code_repository, model_repository):
    # view that links the codes and the models

    sql_create_view = f"""
    REPLACE VIEW {code_model_view} AS
    SEQUENCED VALIDTIME
    SELECT
        MODEL.ID AS ID_MODEL
    ,   CODE.ID AS ID_CODE
    ,	CODE.CODE_TYPE
    ,	CODE.CODE
    ,	MODEL.ARGUMENTS
    ,	MODEL.METADATA AS METADATA_MODEL
    ,	CODE.METADATA AS METADATA_CODE
    FROM
        {model_repository} MODEL
    INNER JOIN	{code_repository} CODE
    ON MODEL.ID_CODE = CODE.ID;
    """

    return sql_create_view


def insert_model(model_id, code_id, arguments, metadata, model_repository):
    # insert a new model
    #
    # model_id : int. id of the new model
    # code_id : id of an existing code
    # arguments : json. two fields: parameters and model_parameters
    # metadata : json. e.g. {"author": "Denis Molin"}

    sql_insert_query = f"""
    CURRENT VALIDTIME INSERT INTO {model_repository}
    (ID, ID_CODE, ARGUMENTS, METADATA) VALUES
    ({model_id}, {code_id}, '{str(arguments).replace("'", '"')}', '{str(metadata).replace("'", '"')}');    
    """

    con = tdml.get_connection()

    con.execute(sql_insert_query)

    return sql_insert_query


def remove_model(model_id, model_repository, **kwargs):
    # remove a model

    sql_query = f"""
    DELETE {model_repository} WHERE ID = {model_id};
    """

    con = tdml.get_connection()

    con.execute(sql_query)

    return sql_query


def update_model_arguments(model_id, arguments, model_repository, **kwargs):
    # update the arguements of an existing model

    sql_query = f"""
    CURRENT VALIDTIME UPDATE {model_repository}
    SET ARGUMENTS = '{str(arguments).replace("'", '"')}'
    WHERE ID = {model_id};
    """

    con = tdml.get_connection()

    con.execute(sql_query)

    return sql_query