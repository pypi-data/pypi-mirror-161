from tkinter.messagebox import NO
from .base import Base

from clickhouse_driver import Client
from .utils.clickhouse import create_table, insert_ddf, insert_df
import pandas as pd
import dask.dataframe as dd

class ClickHouse:
    
    def __init__(self, connection=None):
        if connection is None or type(connection)!= dict:
            """ 
            connection = {
                'host': 'localhost',
                'port': 9090,
                'database': 'warehouse',
                'user': 'clickhouse',
                'password': 'QWER!@#$qwer1234!@#$',
                'settings':{
                    'use_numpy': True
                },
                'secure': False
            }
            """
            raise Exception(f"plase input `connection` or but got connection {type(connection)}")
        client = Client(**connection)
        try:
            client.connection.connect()
        except Exception as e:
            raise e
        self._client = client
        self._connection = connection
        
    def get_or_createTable(self, df=None, tableName=None, key=None):
        if type(df) not in [pd.DataFrame, dd.DataFrame]:
            raise Exception(f"Please input `df=<dask dataframe or pandas dataframe>`, but got {type(df)}")
        if tableName is None:
            raise Exception("Please input `tableName`")
        if key is None:
            raise Exception("Please input `key`")
        
        if key not in df.columns:
            raise Exception(f"key `{key}` not found in columns, columns are {df.columns}")
        status, e = create_table(self._client, df, tableName, key)
        if status == False:
            if e.code == 57:
                print(f"table {tableName} already exists!")
            else:
                raise e
        return tableName
    
    def write(self, df=None, tableName=None, key=None):
        if type(df) not in [pd.DataFrame, dd.DataFrame]:
            raise Exception(f"Please input `df=<dask dataframe or pandas dataframe>`, but got {type(df)}")
        if tableName == None:
            raise Exception(f"Expect `tableName` type str, but got {type(tableName)} please input `tableName` str")
        if key is None:
            raise Exception("Please input `key`")
        if key not in df.columns:
            raise Exception(f"key `{key}` not found in columns, columns are {df.columns}")
        
        if type(df) == dd.DataFrame:
            insert_ddf(connection=self._connection, ddf=df, tableName=tableName)
        elif type(df) == pd.DataFrame:
            insert_df(connection=self._connection, df=df, tableName=tableName)
        else:
            return "Some thing wrong!"
    
    
    def read(self, sqlQuery=None):
        if sqlQuery is None:
            raise Exception(f"plese input `sqlQuery` str but got {type(sqlQuery)}")
        return self._client.query_dataframe(sqlQuery)