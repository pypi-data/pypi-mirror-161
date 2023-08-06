import datetime
import json
import re
import struct
from .tools import bulkload, runquery, runfile

def identity(value):
    return value

def handle_datetimeoffset(dto_value):
    # ref: https://github.com/mkleehammer/pyodbc/issues/134#issuecomment-281739794
    tup = struct.unpack("<6hI2h", dto_value)  # e.g., (2017, 3, 16, 10, 35, 18, 0, -6, 0)
    return datetime.datetime(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6] // 1000,
                             datetime.timezone(datetime.timedelta(hours=tup[7], minutes=tup[8])))


SQL_ERROR_PATTERN = re.compile(r'^\[(.*?)\] \[(.*?)\]\[(.*?)\]\[(.*?)\](.*) \((.*?)\) \((.*?)\)$')

OUTPUT_CONVERTERS = [
    (-150, identity),  # SQL Variant
    (-151, identity),  # SQL Geography
    (-155, handle_datetimeoffset)  # DateTimeOffset
]

class MssqlException(Exception):
    def __init__(self, message, is_user_error, sql_error, sql_state, sql, params=None, resultset_no=None, inner_exception=None):
        self.sql_state = sql_state
        self.message = message
        self.sql_error = sql_error
        self.is_user_error = is_user_error
        self.sql = sql
        self.params = params
        self.inner_exception = inner_exception
        self.resultset_no = resultset_no

    def __repr__(self):
        return json.dumps({'message': self.message,
                           'is_user_error': self.is_user_error,
                           'sql_error': self.sql_error,
                           'sql_state': self.sql_state,
                           'sql': self.sql,
                           'params': self.params,
                           'resultset_no': self.resultset_no})

    __str__ = __repr__

def wrap_pyodbc_error(e, sql=None, params=None, resultset=None):
    m = SQL_ERROR_PATTERN.match(e.args[1]).groups()
    return MssqlException(message=m[4],
                          is_user_error=len(m[5]) == 5 and m[5].sql_error.startswith('50') or m[5] == '201',  # By PMG+ convention, all 50xxx SQL errors are considered user errors
                          sql_error=m[5],
                          sql_state=m[0],
                          sql=sql,
                          params=params,
                          resultset_no=resultset or 0,
                          inner_exception=e)

def connect(connection_string, **kwargs):
    import pyodbc
    cn = pyodbc.connect(connection_string, **kwargs)
    [cn.add_output_converter(conv[0], conv[1]) for conv in OUTPUT_CONVERTERS]
    return cn

def execute(cn, sql, params=None, **kwargs):
    import pyodbc
    try:
        cur = cn.cursor()
        if params:
            cur.execute(sql, params, **kwargs)
        else:
            cur.execute(sql, **kwargs)
        return cur
    except pyodbc.Error as e:
        raise wrap_pyodbc_error(e, sql, params) from e
