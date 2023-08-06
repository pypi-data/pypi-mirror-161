# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 14:44:33 2021

@author: dm250067
"""


from functools import wraps
import teradataml as tdml
import re

def setup_table_for_model_generation(database=re.findall(string=str(tdml.get_context().url),pattern=r'DATABASE=(\w+)')[0]):
    query = f"""
        SEL CAST(DATE '2022-01-01' AS TIMESTAMP) as t0
            , t0 + CAST(9999 AS INTERVAL SECOND(4)) as t1
            , PERIOD(t0, t1) as duration

    """
    tdml.DataFrame.from_query(query).to_sql(schema_name=database, table_name='TABLE_FOR_GENERATION',if_exists='replace')
    return

def InverseHash(subquery, n_factor_hash_map=50,
                database=re.findall(string=str(tdml.get_context().url),pattern=r'DATABASE=(\w+)')[0] ):
    """ A SQL query that compute interger partition ID for each Partition_ID
    values output by the subquery, whatever the data type.

    The results of the query consist of three columns:
        - the Partition_ID column of the input subquery
        - the New_Partition_ID which is an integer
        - the AMP_ID corresponding the retulst of HASHAMP(HASHBUCKET(HASHROW(
            New_Partition_ID)))

    :param subquery: a SQL query as a string that output a column named
    Partition_ID.
    :param n_factor_hash_map: the HASHAMP(HASHBUCKET(HASHROW())) is applied
    to a list of integer from 1 to n_factor_hash_map*(hashamp()+1)
    :return: a SQL query that returns Partition_ID, New_Partition_ID and
    AMP_ID.
    """
    setup_table_for_model_generation(database)

    ref_table = f"""
         (
          SELECT  pd
          FROM {database}.TABLE_FOR_GENERATION
          EXPAND ON duration AS pd BY ANCHOR PERIOD ANCHOR_SECOND
          ) B
     """

    query = f"""
            SELECT
                A2.Partition_ID
            ,	A1.New_Partition_ID
            ,	A1.AMP_ID
        FROM
        (
            SELECT
                I.New_Partition_ID
            ,	I.AMP_ID
            ,	I.row_num4 as row_num
            FROM (
                SELECT
                    B.New_Partition_ID
                ,	B.AMP_ID
                ,	ROW_NUMBER() OVER
                (ORDER BY B.row_key,B.AMP_ID ) as row_num
                ,	ROW_NUMBER() OVER
                (PARTITION BY B.row_key ORDER BY B.AMP_ID  ) as row_num2
                ,	ROW_NUMBER() OVER
                (PARTITION BY B.AMP_ID ORDER BY B.row_key ) as row_num3
                ,	CASE
                    WHEN row_num3 MOD 2 = 1 THEN row_num
                    ELSE row_num-2*row_num2 + hashamp()+2
                    END as row_num4
                FROM
                (
                    SELECT
                        A.RNK as New_Partition_ID
                    ,	A.AMP_ID
                    ,	ROW_NUMBER() OVER
                    ( PARTITION BY A.AMP_ID ORDER BY  A.RNK) as row_key
                    FROM
                    (
                        SELECT
                            ROW_NUMBER() OVER
                            ( ORDER BY pd)
                            as RNK
                        ,   HASHAMP(HASHBUCKET(HASHROW(RNK))) as AMP_ID
                        FROM
                            {ref_table}
                        QUALIFY RNK < 50*(hashamp()+1)+1 -- large enough
                    ) A
                    QUALIFY row_key <
                    (
                        SELECT count(distinct A.Partition_ID)
                        FROM ({subquery}) A)/(hashamp()+1)+1+1
                ) B
            ) I
        ) A1
        ,
        (
            SELECT
                F.Partition_ID
            ,	ROW_NUMBER() OVER (ORDER BY F.Partition_size DESC) as row_num
            FROM (
                SELECT
                    A.Partition_ID
                ,	count(*) as Partition_size
                FROM ({subquery}) A
                GROUP BY 1
            ) F
        ) A2
        WHERE A1.row_num = A2.row_num
        """
    return query


def EquallyDistributed(func):
    """A decorator that reverses the hash function to equally distributed
    partitions among the AMP, so that we have the same number of partition
    per AMP."""
    # Define the wrapper function to return.
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the decorated function and store the result.
        subquery_dataset, features = func(*args, **kwargs)

        # Get the conversion of the Partition_ID to a New_Partition_ID that
        # is an integer that fits better with the hash function
        subquery_redistribution = InverseHash(subquery_dataset)

        # Rewrite the query
        query = f"""
        SELECT
        B.New_Partition_ID as Partition_ID
        ,   A.ID
        ,   {',  '.join(features)}
        FROM ({subquery_dataset}) A
        , ({subquery_redistribution}) B
        WHERE A.Partition_ID = B.Partition_ID
        """
        return query, features
    return wrapper


def PlotDistribution(schemaT, table_name, partition='partition_id'):
    """ Get the query that assess the data distribution of a table.


    Parameters
    ----------
    schemaT : str
        database name.
    table_name : str
        table name.
    partition : str, optional
        the columns to partition the data. The default is 'partition_id'.

    Returns
    -------
    the query to get the data distribution.

    """
    query = f"""
    SELECT
        hashamp(hashbucket(hashrow({partition}))) as AMP_ID
    ,   count(distinct {partition}) as Nb_Partitions
    ,   count(*) as Nb_rows
    FROM {schemaT}.{table_name}
    GROUP BY 1
    ORDER BY 3 DESC
    """

    return query

