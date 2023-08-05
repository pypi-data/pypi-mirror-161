from pyg_base import cache, Dict, is_pd, is_arr, is_dict, dictable
from pyg_sql._sql_table import sql_table, _pairs2connection
from pyg_encoders import encode, cell_root, root_path, root_path_check, dictable_decoded, WRITERS
import pandas as pd
import pickle

sql_table_ = cache(sql_table)
_sql = '.sql'
_dictable = '.dictable'
_dictable_decoded = encode(dictable_decoded)
_key = 'key'
_data = 'data'

def sql_binary_store(path):
    """
    splits a path which resembles a sql-alchemy connection string, to its bits

    Parameters
    ----------
    path : str
        extended connection string.

    Returns
    -------
    dict
        various connection parameters. specifically, the cursor parameter actually generates the table
    """
    u, p = path.split('//')
    ps = p.split('/')
    server = ps[0]
    params = ps[1]
    if '?' in params:
        db, prm = params.split('?')
        connections = _pairs2connection(*prm.split('&'))
    else:
        db = params
        connections = {}
    doc = connections.pop('doc', 'true')
    doc = dict(true = True, false = False).get(doc.lower(), doc)        
    url = '%s//%s/%s'%(u, server, params)
    table = ps[2].split('/')[0]
    root = '/'.join(ps[3:])
    if '.' in table:
        schema, table = table.split('.')
    else:
        schema = None
    schema = connections.pop('schema', schema)
    cursor = sql_table(table = table, db = db, schema = schema, pk = _key, 
                        non_null = {_data : bin}, doc = doc)
    connections.update(dict(url = url, server = server, schema  = schema, cursor = cursor, root = root, table = table))
    return Dict(connections)


def sql_dumps(obj, path):
    """
    >>> from pyg import *
    >>> path = 'mssql+pyodbc://localhost/test_db/xxx.test_table/key'
    >>> self = sql_binary_store(path).cursor
    >>> self.deleted
    >>> obj = pd.Series([1,2,3])
    >>> sql_dumps(obj, path)
    >>> sql_loads(path)
    Parameters
    ----------
    obj : object
        item to be pickled into binary.
    path : str
        path sqlalchemy-like to save the pickled binary in.

    Returns
    -------
    string 
        path

    """
    res = sql_binary_store(path)
    data = pickle.dumps(obj)
    cursor = res.cursor
    root = res.root
    # print('dumping into...\n', cursor)
    cursor.update_one({_key : root, _data : data})
    # print(cursor)
    return path

def sql_loads(path):
    res = sql_binary_store(path)
    cursor = res.cursor
    root = res.root
    row = cursor.inc(**{_key :root})
    if len(row) == 0:
        # print('no documents found in...\n', row)
        raise ValueError('no document found in %s' %(res-'cursor'))
    elif len(row) > 1:
        raise ValueError('multiple documents found \n%s'%row)
    else:
        # print('loading from...\n', row)
        data = row[0][_data]
        obj = pickle.loads(data)
        return obj
    
_sql_loads = encode(sql_loads)

def sql_encode(value, path):
    """
    encodes a single DataFrame or a document containing dataframes into a an abject of multiple pickled files that can be decoded

    Parameters:
    ----------
    value : document or dataframe
        value to be encoded inside a sql database
        
    path : str
        a sqlalchemy-like string
        
    Example: writing a single dataframe
    --------
    >>> from pyg import * 
    >>> value = pd.Series([1,2])
    >>> path = 'mssql+pyodbc://localhost/database_here?doc=false/xyz.table_name/root_of_doc'
    >>> res = sql_encode(value, path)
    >>> table = sql_table(db = 'database_here', schema = 'xyz', table = 'table_name')
    >>> assert len(table.inc(key = 'root_of_doc'))>0
    >>> sql_loads(path)
    
    Example: writing a document
    ---------------------------
    >>> from pyg import * 
    >>> value = dict(a = pd.Series([1,2]), b = pd.Series([3,4]))
    >>> path = 'mssql+pyodbc://localhost/database_here?doc=false/xyz.table_name/root_of_doc'
    >>> res = sql_encode(value, path)
    >>> table = sql_table(db = 'database_here', schema = 'xyz', table = 'table_name')
    >>> keys = table.distinct('key')
    >>> assert 'root_of_doc/a' in keys and 'root_of_doc/b' in keys    
    >>> assert eq(value['a'],sql_loads(path+'/a'))
    """
    if path.endswith(_sql):
        path = path[:-len(_sql)]
    if path.endswith('/'):
        path = path[:-1]
    if is_pd(value) or is_arr(value):
        path = root_path_check(path)
        return dict(_obj = _sql_loads, path = sql_dumps(value, path))       
    elif is_dict(value):
        res = type(value)(**{k : sql_encode(v, '%s/%s'%(path,k)) for k, v in value.items()})
        if isinstance(value, dictable):
            df = pd.DataFrame(res)
            return dict(_obj = _dictable_decoded, 
                        path =  sql_dumps(df, path + _dictable))
        return res
    elif isinstance(value, (list, tuple)):
        return type(value)([sql_encode(v, '%s/%i'%(path,i)) for i, v in enumerate(value)])
    else:
        return value
    
def sql_write(doc, root = None):
    """
    writes dataframes within a document into a sql.
    
    :Example:
    ---------
    >>> from pyg import * 
    >>> from pyg_sql._sql_writer import path_to_connection
    >>> db = partial(sql_table, 
                     table = 'tickers', 
                     db = 'bbgs', 
                     pk = ['ticker', 'item'], 
                     server = 'localhost', 
                     writer = 'mssql+pyodbc://localhost/bbgs?driver=ODBC+Driver+17+for+SQL+Server&doc=false/bbg_data/%ticker/%item.sql', 
                     doc = True)
    >>> path = db().writer
    >>> res = path_to_connection(path)
    >>> ticker = 'CLA Comdty'
    >>> item = 'price'
    >>> doc = db_cell(passthru, data = pd.Series([1,2,3],drange(2)), 
                      array = np.array([1,2,3]),
                      list_of_values = [np.array([1,2,]), pd.DataFrame([1,2])],
                      ticker = ticker, item = item, db = db)
    >>> doc = doc.go()
    
    >>> get_cell('tickers', 'bbgs', server = 'localhost', ticker = ticker, item = item)
    """
    root = cell_root(doc, root)
    if root is None:
        return doc
    path = root_path(doc, root)
    return sql_encode(doc, path)
    
WRITERS[_sql] = sql_write


