# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 09:15:23 2021

@author: dm250067
"""


def CreateViewFromTable(schemaT, table_name, schemaV=None, view_name=None):
    """ Create a view corrsponding to a table.

    Parameters
    ----------
    schemaT : str
        database name containing the table.
    table_name : str
        table name we want to put behind the view.
    schemaV : str, optional
        database name that will contain the view when different from schemaT.
        The default is None.
    view_name : str, optional
        name of the view. By default it is V_+table_name. The default is None.

    Returns
    -------
    the query to build the view.

    """
    if schemaV is None:
        schemaV = schemaT

    if view_name is None:
        view_name = 'V_'+table_name

    query = f"""REPLACE VIEW {schemaV}.{view_name}
    AS
    SELECT * FROM {schemaT}.{table_name}"""

    return query


def QueryToTable(schema, table_name, query, primary_index='PARTITION_ID'):
    """
    An alternative to the to_sql function of teradataml.

    Parameters
    ----------
    schema : str
        the database that will receive the data.
    table_name : str
        the table name that will receive the data.
    query : str
        the SQL query to build the data.
    primary_index : str, optional
        DESCRIPTION. The default is 'PARTITION_ID'.

    Returns
    -------
    query : str
        the query to create the table.

    """

    query = f"""
        CREATE MULTISET TABLE {schema}.{table_name}, FALLBACK ,
                     NO BEFORE JOURNAL,
                     NO AFTER JOURNAL,
                     CHECKSUM = DEFAULT,
                     DEFAULT MERGEBLOCKRATIO,
                     MAP = TD_MAP1 AS (
        {query}
        ) WITH DATA
            PRIMARY INDEX (PARTITION_ID)
        """
    return query


def ConvertDictToSQL(**kwargs):
    """
    Convert a dictionary with keys corresponding to the column names and
    values to the data type in the SQL format for table creation.

    example: {'ID':'INTEGER', 'NAME':'VARCHAR(10)'}

    Parameters
    ----------
    **kwargs : kwargs
        DESCRIPTION.

    Returns
    -------
    the string corresponding to the SQL syntax, with comma separation.

    """

    return ',\n'.join([k+'\t'+kwargs[k] for k in kwargs
                       if k.lower().replace(' ', '') != 'primaryindex'])
