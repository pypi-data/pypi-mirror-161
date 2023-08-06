import teradataml as tdml

def preparedataset_from_teradata_dataframe(dataset,ID_Columns,Partition,FoldID=None):
    # - dataset is a teradataml dataframe.
    # - ID_Columns is the list of columns that is unique per partition
    # - Partition is the list of columns defining a partition
    # - FoldID define what is train or test data or multiple folds
    # This function add three columns to the dataset:
    # - STO_ID
    # - STO_PARTITION_ID (a JSON)
    # - STO_FOLD_ID

    cols = [str.lower(x) for x in dataset.columns]
    for c in ['STO_ID','STO_PARTITION_ID','STO_FOLD_ID']:
        if c in cols:
            print(f'{c} already exists in your dataset. Please rename or remove this column.')
            return

    if FoldID:
        new_cols = {
            'STO_ROW_ID'       : tdml.sqlalchemy.literal_column(f"CAST(JSON_COMPOSE({','.join(Partition+ID_Columns)}) AS VARCHAR(2000) CHARACTER SET UNICODE)"),
            'STO_PARTITION_ID' : tdml.sqlalchemy.literal_column(f"CAST(JSON_COMPOSE({','.join(Partition)}) AS VARCHAR(2000) CHARACTER SET UNICODE)"),
            'STO_FOLD_ID'      : FoldID

        }
    else:
        new_cols = {
            'STO_ROW_ID': tdml.sqlalchemy.literal_column(
                f"CAST(JSON_COMPOSE({','.join(Partition + ID_Columns)}) AS VARCHAR(2000) CHARACTER SET UNICODE)"),
            'STO_PARTITION_ID': tdml.sqlalchemy.literal_column(
                f"CAST(JSON_COMPOSE({','.join(Partition)}) AS VARCHAR(2000) CHARACTER SET UNICODE)")

        }

    dataset_training = dataset.assign(**new_cols)


    return dataset_training


def preparedataset_from_table(schema, view_name, input_table_name, input_schema_name, ID_Columns,Partition,FoldID=None):
    # - schema is the schema of the output view.
    # - view_name is the name of the output view
    # - input_table_name is the complete name schema.table_name of the dataset
    # - ID_Columns is the list of columns that is unique per partition
    # - Partition is the list of columns defining a partition
    # - FoldID define what is train or test data or multiple folds
    # This function add three columns to the dataset:
    # - STO_ID
    # - STO_PARTITION_ID (a JSON)
    # - STO_FOLD_ID


    columns = tdml.DataFrame(tdml.in_schema(input_schema_name,input_table_name)).columns
    {','.join([x for x in columns if x.lower() != FoldID.lower()])}
    query = f"""
        REPLACE VIEW {schema}.{view_name} AS
        {prepared_new_colums_sql(input_schema_name,input_table_name,ID_Columns,Partition,FoldID)}
    """

    tdml.get_context().execute(query)

    return tdml.DataFrame(tdml.in_schema(schema,view_name))

def prepared_new_colums_sql(input_schema_name,input_table_name,ID_Columns,Partition,FoldID=None):

    if FoldID:
        query = f"""
             SEL
                 A.*
             ,   CAST(JSON_COMPOSE({','.join(Partition + ID_Columns)}) AS VARCHAR(2000) CHARACTER SET UNICODE) AS STO_ROW_ID
             ,   CAST(JSON_COMPOSE({','.join(Partition)}) AS VARCHAR(2000) CHARACTER SET UNICODE) AS STO_PARTITION_ID
             ,   {FoldID} AS STO_FOLD_ID
             FROM {input_schema_name}.{input_table_name} A
         """
    else:
        query = f"""
             SEL
                 A.*
             ,   CAST(JSON_COMPOSE({','.join(Partition + ID_Columns)}) AS VARCHAR(2000) CHARACTER SET UNICODE) AS STO_ROW_ID
             ,   CAST(JSON_COMPOSE({','.join(Partition)}) AS VARCHAR(2000) CHARACTER SET UNICODE) AS STO_PARTITION_ID
             FROM {input_schema_name}.{input_table_name} A
         """
    return query