import teradataml as tdml


def create_code_repository(code_repository):
    # sql query that creates the sto code repository table
    sql_create_table = f"""
        CREATE MULTISET TABLE {code_repository},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            ID BIGINT,
            CODE_TYPE VARCHAR(255) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
            CODE BLOB,
            METADATA JSON(32000), 
            ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
            PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME	
        )
        PRIMARY INDEX (ID);
    """

    return sql_create_table

def insert_code(code_id, code_repository, filename, metadata, model_type='python class MyModel'):
    # insert the code in the code_repository table
    #
    # code_id : int. the unique ID of the repo.
    # code_repository : str. the name of the sto code repository table
    # filename : the filename of the python file containing the code
    # metadata : json format. e.g.'{"author": "Denis Molin"}'
    # model_type : str. default is 'python class MyModel'

    sql_query = f"""
    CURRENT VALIDTIME INSERT INTO {code_repository}
    (ID, CODE_TYPE, CODE, METADATA)
     VALUES
    ({code_id}, '{model_type}', ?, '{str(metadata).replace("'", '"')}');
    """

    with open(filename, 'r') as file:
        code = file.read()

    con = tdml.get_connection()

    con.execute(sql_query, code)

    return sql_query


def remove_code(code_id, code_repository, **kwargs):
    # remove a deployed code

    sql_query = f"""
    DELETE {code_repository} WHERE ID = {code_id};
    """

    con = tdml.get_connection()

    con.execute(sql_query)

    return sql_query


def update_code(code_id, code_repository, filename, **kwargs):
    # update an existing code

    sql_query = f"""
    CURRENT VALIDTIME UPDATE {code_repository}
    SET CODE   = ?
    WHERE ID = {code_id};
    """

    with open(filename, 'r') as file:
        code = file.read()

    con = tdml.get_connection()

    con.execute(sql_query, code.encode())

    return sql_query


