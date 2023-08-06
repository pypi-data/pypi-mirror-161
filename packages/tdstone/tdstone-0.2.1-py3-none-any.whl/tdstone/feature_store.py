from tdstone.utils import execute_querydictionary
import teradataml as tdml
import re


def create_features_table(schema_name,table_root_name):


    sql_query_float = f"""
    CREATE TABLE {schema_name}.EFS_{table_root_name}_FLOAT 
    (
        ID BIGINT
    ,   CALCULATED_FEATURE_ID BIGINT
    ,   Feature_Value FLOAT
    ,   ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL
    ,   ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL
    ,   PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
    )
    PRIMARY INDEX (ID)
    PARTITION BY CALCULATED_FEATURE_ID;
    """

    sql_query_integer = f"""
    CREATE TABLE {schema_name}.EFS_{table_root_name}_INTEGER
    (
        ID BIGINT
    ,   CALCULATED_FEATURE_ID BIGINT
    ,   Feature_Value BIGINT
    ,   ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL
    ,   ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL
    ,   PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
    )
    PRIMARY INDEX (ID)
    PARTITION BY CALCULATED_FEATURE_ID;
    """

    sql_query_varchar = f"""
    CREATE TABLE {schema_name}.EFS_{table_root_name}_VARCHAR
    (
        ID BIGINT
    ,   CALCULATED_FEATURE_ID BIGINT
    ,   Feature_Value VARCHAR
    ,   ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL
    ,   ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL
    ,   PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
    )
    PRIMARY INDEX (ID)
    PARTITION BY CALCULATED_FEATURE_ID;
    """

    try:
        tdml.get_context().execute(sql_query_float)
    except:
        print(f'TABLE EFS_{table_root_name}_FLOAT already exists')
    try:
        tdml.get_context().execute(sql_query_integer)
    except:
        print(f'TABLE EFS_{table_root_name}_INTEGER already exists')
    try:
        tdml.get_context().execute(sql_query_varchar)
    except:
        print(f'TABLE EFS_{table_root_name}_VARCHAR already exists')

    return

####################################### FEATURE CATALOG ######################################
def create_feature_catalog(feature_catalog):
    # sql query that creates the feature catalog table
    sql_create_table = f"""
        CREATE MULTISET TABLE {feature_catalog},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
    (
        FEATURE_ID BIGINT,
        OBJECT_CONCEPT_ID BIGINT,
        LOCATION VARCHAR(32000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
    )
    PRIMARY INDEX (FEATURE_ID);
    """

    return sql_create_table


def create_feature_description(feature_description):
    # sql query that creates the feature description
    sql_create_table = f"""
        CREATE MULTISET TABLE {feature_description},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
    (
        FEATURE_ID BIGINT,
        BUSINESS_NAME VARCHAR(32000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
        DESCRIPTION VARCHAR(32000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
    )
    PRIMARY INDEX (FEATURE_ID);
    """

    return sql_create_table


def create_object_description(object_description):
    # sql query that creates the feature description
    sql_create_table = f"""
        CREATE MULTISET TABLE {object_description},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
    (
        OBJECT_CONCEPT_ID BIGINT,
        BUSINESS_NAME VARCHAR(32000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
        DATASET VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL,
        DESCRIPTION VARCHAR(32000) CHARACTER SET UNICODE NOT CASESPECIFIC NOT NULL
    )
    PRIMARY INDEX (OBJECT_CONCEPT_ID)
    """

    return sql_create_table


def create_view_feature_catalog(feature_catalog_view,
                                feature_catalog,
                                feature_description,
                                object_description
                                ):
    # sql query that creates view for the feature catalog, that
    # joins the feature catalog and the feature and object description
    # tables
    sql_create_view = f"""
    REPLACE VIEW {feature_catalog_view} AS
    SEL 
        CATALOG.*
    ,	FEATURE.BUSINESS_NAME AS FEATURE_NAME
    ,	OBJECT_CONCEPT.BUSINESS_NAME AS OBJECT_CONCEPT_NAME
    ,   OBJECT_CONCEPT.DATASET AS DATASET
    FROM {feature_catalog} CATALOG
    LEFT JOIN {feature_description} FEATURE
    ON CATALOG.FEATURE_ID = FEATURE.FEATURE_ID
    LEFT JOIN {object_description} OBJECT_CONCEPT
    ON CATALOG.OBJECT_CONCEPT_ID = OBJECT_CONCEPT.OBJECT_CONCEPT_ID;
    """

    return sql_create_view

####################################### CALCULATED FEATURE CATALOG ######################################
def create_calculated_feature_catalog(calculated_feature_catalog):
    # sql query that creates the calculated feature catalog table
    sql_create_table = f"""
        CREATE MULTISET TABLE {calculated_feature_catalog},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
        (
            CALCULATED_FEATURE_ID BIGINT,
            FEATURE_ID BIGINT,
            ID_PROCESS BIGINT
        )
        PRIMARY INDEX (FEATURE_ID);
    """

    return sql_create_table


def create_calculated_feature_view(calculated_feature_view, feature_catalog_view, calculated_feature_catalog):
    # create a view that links the features and the calculated features

    sql_create_view = f"""
    -- GET THE CALCULATED FEATURE ID FROM THE FEATURE NAME CALCULATED WITH A GIVEN PROCESS
    REPLACE VIEW {calculated_feature_view} AS
    SELECT
        FEATURE.FEATURE_NAME
    ,	CALC_FEATURE.CALCULATED_FEATURE_ID
    ,	FEATURE.LOCATION
    ,	CALC_FEATURE.ID_PROCESS
    FROM {feature_catalog_view} FEATURE
    LEFT JOIN {calculated_feature_catalog} CALC_FEATURE
    ON FEATURE.FEATURE_ID = CALC_FEATURE.FEATURE_ID;    
    """

    return sql_create_view


####################################### PROCESS FEATURE ######################################

def create_process_catalog(process_catalog):
    # sql query that creates the process catalog table
    sql_create_table = f"""
        CREATE MULTISET TABLE {process_catalog},
        FALLBACK,
        NO BEFORE JOURNAL,
        NO AFTER JOURNAL,
        CHECKSUM = DEFAULT,
        DEFAULT MERGEBLOCKRATIO,
        MAP = TD_MAP1
    (
        ID_PROCESS BIGINT,
        PROCESS_TYPE VARCHAR(255) CHARACTER SET UNICODE NOT CASESPECIFIC,
        ID_MAPPER BIGINT,
        MODEL_CODE_VIEW VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC,
        FOLD VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC,

        PREPARED_DATASET VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC,
        ON_CLAUSE VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC,
        RESULTS VARCHAR(2000) CHARACTER SET UNICODE NOT CASESPECIFIC,

        STO_DATABASE VARCHAR(255) CHARACTER SET UNICODE NOT CASESPECIFIC,

        ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
        ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
    )
    PRIMARY INDEX (ID_PROCESS);
    """

    return sql_create_table



def insert_new_process(id_process, process_type, id_mapper, model_code_view,  prepared_dataset, on_clause, results,
                       sto_database, process_catalog,fold=None, **kwargs):
    # add or update a process
    #
    # id_process : int. id of the process
    # process_type : str. process type e.g. view, sto_feature, sto_training, sto_scoring
    # input_object : str. name of the view/table used as a process input
    # process_catalog : str. name of the process catalog table

    res = tdml.get_context().execute(f'sel count(*) from {process_catalog} where ID_PROCESS = {id_process}').fetchall()[0][0]
    if res == 0:
        sql_insert_query = f"""
        CURRENT VALIDTIME INSERT INTO {process_catalog}
        (ID_PROCESS, PROCESS_TYPE, ID_MAPPER, MODEL_CODE_VIEW, FOLD, PREPARED_DATASET, ON_CLAUSE, RESULTS, STO_DATABASE )
        VALUES
        ({id_process}, '{process_type}', {id_mapper},'{model_code_view}','{fold}',
        '{prepared_dataset}', '{on_clause}', '{results}', '{sto_database}'
        );
        """
    elif len(fold)>0:
        sql_insert_query = f"""
        CURRENT VALIDTIME UPDATE {process_catalog}
        SET
            PROCESS_TYPE = '{process_type}'
        ,   ID_MAPPER = '{id_mapper}'
        ,   MODEL_CODE_VIEW = '{model_code_view}'
        ,   FOLD = '{fold}'
        ,   PREPARED_DATASET = '{prepared_dataset}'
        ,   ON_CLAUSE = '{on_clause}'
        ,   RESULTS = '{results}'
        ,   STO_DATABASE = '{sto_database}'     
        WHERE ID_PROCESS = {id_process}
        """
    else:
        sql_insert_query = f"""
        CURRENT VALIDTIME UPDATE {process_catalog}
        SET
            PROCESS_TYPE = '{process_type}'
        ,   ID_MAPPER = '{id_mapper}'
        ,   MODEL_CODE_VIEW = '{model_code_view}'
        ,   PREPARED_DATASET = '{prepared_dataset}'
        ,   ON_CLAUSE = '{on_clause}'
        ,   RESULTS = '{results}'
        ,   STO_DATABASE = '{sto_database}'       
        WHERE ID_PROCESS = {id_process}
        """

    con = tdml.get_connection()

    con.execute(sql_insert_query)

    return sql_insert_query

class feature_store():

    def __init__(self,database,
                 SEARCHUIFDBPATH=re.findall(string=str(tdml.get_context().url),pattern=r'DATABASE=(\w+)')[0],
                 rootname='FS'):
        self.database = database
        self.rootname = rootname
        self.feature_catalog = f'{database}.{rootname}_FEATURE_CATALOG'
        self.feature_description = f'{database}.{rootname}_FEATURE_DESCRIPTION'
        self.object_description = f'{database}.{rootname}_OBJECT_DESCRIPTION'
        self.feature_catalog_view = f'{database}.V_{rootname}_FEATURE_CATALOG'
        self.calculated_feature_catalog = f'{database}.{rootname}_CALCULATED_FEATURE_CATALOG'
        self.calculated_feature_view = f'{database}.V_{rootname}_CALCULATED_FEATURE_CATALOG'
        self.process_catalog = f'{database}.{rootname}_PROCESS_CATALOG'
        self.process_input_output = f'{database}.{rootname}_PROCESS_INPUT_OUTPUT'

    def setup(self):
        sql_queries = {}
        sql_queries['feature_catalog'] = create_feature_catalog(self.feature_catalog)
        sql_queries['feature_description'] = create_feature_description(self.feature_description)
        sql_queries['object_description'] = create_object_description(self.object_description)
        sql_queries['feature_catalog_view'] = create_view_feature_catalog(self.feature_catalog_view,
                                                                          self.feature_catalog,
                                                                          self.feature_description,
                                                                          self.object_description
                                                                          )

        sql_queries['calculated_feature_catalog'] = create_calculated_feature_catalog(self.calculated_feature_catalog)
        sql_queries['calculated_feature_view'] = create_calculated_feature_view(self.calculated_feature_view,
                                                                                self.feature_catalog_view,
                                                                                self.calculated_feature_catalog)
        sql_queries['process_catalog'] = create_process_catalog(self.process_catalog)

        execute_querydictionary(sql_queries)
        return

    def clean(self):
        tdml.db_drop_view(self.calculated_feature_view.split('.')[1])
        tdml.db_drop_view(self.feature_catalog_view.split('.')[1])


        tdml.db_drop_table(self.object_description.split('.')[1])
        tdml.db_drop_table(self.feature_description.split('.')[1])
        tdml.db_drop_table(self.feature_catalog.split('.')[1])


        tdml.db_drop_table(self.calculated_feature_catalog.split('.')[1])
        tdml.db_drop_table(self.process_catalog.split('.')[1])


        return

    def register_object(self,ID, object_feature):
        # create an object with its description
        # ID : unique ID of the object
        # object: a dictionary with the name and description fields
        # object_description_table : the destination table

        sql_insert = f"""
        INSERT INTO {self.object_description} 
        (OBJECT_CONCEPT_ID, BUSINESS_NAME, DESCRIPTION) VALUES
        ({ID}, 
        '{object_feature['name']}',
        '{object_feature['description']}');
        """

        create_features_table(self.database,object_feature['name'])

        tdml.get_context().execute(sql_insert)

        return


    def register_feature(self,object_name, id_feature, feature_name, feature_description, data_type, **kwargs):

        sql_insert_1 = f"""
        INSERT INTO {self.feature_description} 
        (FEATURE_ID, BUSINESS_NAME, DESCRIPTION) VALUES
        ({id_feature}, 
        '{feature_name}',
        '{feature_description}');
        """

        sql_insert_2 = f"""
        INSERT INTO {self.feature_catalog} 
        (FEATURE_ID, OBJECT_CONCEPT_ID, LOCATION) 
        SEL A.FEATURE_ID, B.OBJECT_CONCEPT_ID, 'EFS_{object_name}_{data_type}'
        FROM {self.feature_description} A,
        {self.object_description} B
        WHERE A.FEATURE_ID = '{id_feature}' AND B.BUSINESS_NAME = '{object_name}';
        """

        tdml.get_context().execute(sql_insert_1)
        tdml.get_context().execute(sql_insert_2)

        return



    def remove_existing_process(self,id_process,  **kwargs):
        # add a process
        #
        # id_process : int. id of the process
        # process_type : str. process type e.g. view, sto_feature, sto_training, sto_scoring
        # input_object : str. name of the view/table used as a process input
        # process_catalog : str. name of the process catalog table

        sql_insert_query = f"""
        DELETE {self.process_catalog}
        WHERE ID_PROCESS = {id_process};

        DELETE {self.calculated_feature_catalog}
        WHERE ID_PROCESS = {id_process};
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        return sql_insert_query

    def insert_new_calculated_feature(self,id_process, map_features_process, **kwargs):
        # add new calculated features
        #
        # map_features_process : list of dictionary. [{CALCULATED_FEATURE_ID, FEATURE_NAME, ID_PROCESS}]
        # calculated_feature_catalog : str. calcultated feature catalog table name.

        # upload the map_feature_process dataframe in a volatile table
        df = pd.DataFrame(map_features_process)
        df['ID_PROCESS'] = id_process
        tmp_table_name = 'tmp_' + str(uuid.uuid1()).replace('-', '_')
        tdml.copy_to_sql(df=df,
                         if_exists='replace',
                         schema_name=self.calculated_feature_catalog.split('.')[0],
                         table_name=tmp_table_name,
                         temporary=True
                         )

        # insert the calculated features
        sql_insert_query = f"""
        INSERT INTO {self.calculated_feature_catalog}
        (CALCULATED_FEATURE_ID, FEATURE_ID, ID_PROCESS)
        SEL 
            A.CALCULATED_FEATURE_ID
        ,   B.FEATURE_ID
        ,   A.ID_PROCESS
        FROM {tmp_table_name} A
        , {self.feature_catalog_view} B
        WHERE A.FEATURE_NAME = B.FEATURE_NAME;
        """

        con = tdml.get_connection()

        con.execute(sql_insert_query)

        con.execute(f'DROP TABLE {tmp_table_name}')

        return

    def get_process_parameters(self, id_process):

        sql_sel_query = f"""
            SEL 
                ID_PROCESS
            ,   PROCESS_TYPE 
            ,   ID_MAPPER 
            ,   MODEL_CODE_VIEW 
            ,   FOLD
            ,   PREPARED_DATASET 
            ,   ON_CLAUSE 
            ,   RESULTS 

            ,   STO_DATABASE 
            FROM {self.process_catalog}
            WHERE ID_PROCESS = {id_process};
        """

        con = tdml.get_connection()

        res_ = con.execute(sql_sel_query).fetchall()[0]
        keys_ = ['id_process',
                 'process_type',
                 'id_mapper',
                 'model_code_view',
                 'fold',
                 'prepared_dataset',
                 'on_clause',
                 'results',
                 'sto_database'
                ]

        res = {keys_[i]:v for i,v in enumerate(res_)}
        res['process_catalog'] = self.process_catalog
        try:
            res['results'] = res['results'].replace('_FLOAT','').replace('_INTEGER','')
        except Exception as e:
            res['results'] = res['results']

        return res

    def list_process(self):

        sql_sel_query = f"""
            SEL 
                *
            FROM {self.process_catalog}
        """
        return tdml.DataFrame.from_query(sql_sel_query)

    def list_current_process(self):

        sql_sel_query = f"""
            CURRENT VALIDTIME
            SEL 
                *
            FROM {self.process_catalog}
        """
        return tdml.DataFrame.from_query(sql_sel_query)