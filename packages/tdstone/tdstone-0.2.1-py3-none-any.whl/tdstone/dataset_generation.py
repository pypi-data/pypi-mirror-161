from tdstone.data_distribution import EquallyDistributed,setup_table_for_model_generation
import teradataml as tdml
import re



def GenerateDataSet(n_x=9, n_f=1, n_partitions=2, n_rows=5,
                    noise_classif=0.01,
                    train_test_split_ratio = 0.2,
                    database=re.findall(string=str(tdml.get_context().url),pattern=r'DATABASE=(\w+)')[0] ):
    """ A SQL query that generates in database a multi-partitioned dataset.

    For each partition, a set of independent random variables are generated.
    From these variables, two variables are calculated:
        - Y1 : as a linear combination of the continuous variable. The coef-
        ficients are constant all over the partition, i.e. a linear model is
        expected to fit the Y1 from the float features. The linear coefficients
        are generated randomly.
        - Y2 : is calculated from Y1 as equal to 1 when > than the average of
        Y1 over the partition, and 0 otherwise.
    As a matter of fact, Y1 can be used to train regression models and Y2 clas-
    sification models.

    :param n_x: number of float features following. These features are
    standardized with a zero mean.
    :param n_f: number of 2-level categorical variables. Levels are 0 and 1.
    :param n_partitions: number of partitions.
    :param n_rows: number of rows per partitions. All partitions exhibit the
    same number of rows.
    :param N: this number should be should be an integer greater than n_rows
    divided by the number of rows in dbc_columns
    :param noise_classif: add a noise to the classification
    :return: a SQL query and the column names.
    """

    N = int(n_partitions * n_rows / 99999 + 1)

    setup_table_for_model_generation(database)
    if n_x < 2:
        raise ValueError('The number of float features must be > 1 !')

    if n_f < 1:
        raise ValueError('The number of categorical feature must be > 0 !')

    if n_partitions < 1:
        raise ValueError('The number of partition must be > 0 !')

    if n_rows < 5:
        raise ValueError('The number of rows per partition must be > 4 !')

    random_x = """sqrt(-2.0*ln(CAST(RANDOM(1,999999999) AS FLOAT)/1000000000))
    * cos(2.0*3.14159265358979323846 * CAST(RANDOM(0,999999999) AS FLOAT)
    /1000000000)"""
    random_f = "RANDOM(0,1)"
    random_c = """RANDOM(0,1)*sqrt(-2.0 * ln(CAST(RANDOM(1,999999999) AS
    FLOAT)/1000000000)) * cos(2.0*3.14159265358979323846 *
    CAST(RANDOM(0,999999999) AS FLOAT)/1000000000)"""

    X_names = ['X'+str(i+1) for i in range(n_x)]
    F_names = ['flag'+str(i+1) for i in range(n_f)]
    if len(F_names) == 1:
        F_names = ['flag']

    ref_table = f"""
        (
         SELECT  pd
         FROM {database}.TABLE_FOR_GENERATION
         EXPAND ON duration AS pd BY ANCHOR PERIOD ANCHOR_SECOND
         ) B
    """

    query_long = f"""
            select
                row_number() over (
                    order by  pd) as RNK
            from
                {ref_table}"""

    if N > 1:
        for iter in range(N-1):
            query_long += f"""
                UNION ALL
                select
                row_number() over (
                    order by  pd)
                + (SEL count(*) FROM {ref_table})*({iter}+1)
                as RNK
            from
                {ref_table}"""

    if train_test_split_ratio > 1:
        train_test_split_condition = f"""CASE WHEN ID<{train_test_split_ratio} THEN 'train' ELSE 'test' END"""
    else:
        train_test_split_condition = f"""CASE WHEN ID<{train_test_split_ratio*n_rows} THEN 'train' ELSE 'test' END"""

    query = f"""
        SELECT AA.*
        , CASE WHEN (AA.Y1 + {random_x}*{noise_classif}> AVG(AA.Y1)
                     OVER (PARTITION BY AA.PARTITION_ID))
        THEN 1 ELSE 0 END AS Y2
        , {train_test_split_condition} as FOLD
        FROM (
        SELECT
            A.RNK as Partition_ID
        ,   B.RNK as "ID"
        ,   {', '.join([random_x+' as '+X_names[i] for i in range(n_x)])}
        ,   {','.join([random_f+' as '+F_names[i] for i in range(n_f)])}
        ,   {'+'.join(['C1_'+str(i+1)+'*'+X_names[i] for i in range(n_x)])}
        as Y1
        FROM
            (
            -- partitions
            select
                row_number() over (
                    order by  pd) as RNK
            ,   {', '.join([random_c+' as C1_'+str(i+1) for i in range(n_x)])}
            from
                {ref_table}
            qualify RNK < {n_partitions}+1
            ) A
        ,
            (
            -- inside partitions
            select * from
                (
                    {query_long}
                ) DD
            where DD.RNK < {n_rows}+1
            ) B
            ) AA
        """

    return query, X_names+F_names+['Y1', 'Y2']+['FOLD']


GenerateEquallyDistributedDataSet = EquallyDistributed(GenerateDataSet)

