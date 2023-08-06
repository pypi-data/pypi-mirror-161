import teradataml as tdml

def execute_querydictionary(query_dict):
    con_tdml = tdml.get_context()
    for k in query_dict.keys():
        con_tdml.execute(query_dict[k])
    return