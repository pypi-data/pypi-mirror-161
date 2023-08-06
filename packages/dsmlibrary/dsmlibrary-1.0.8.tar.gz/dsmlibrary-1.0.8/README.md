# DSM Library

## DataNode
0. init DataNode
```python
from dsmlibrary.datanode import DataNode 

data = DataNode(token)
```
1. upload file
```python
data.upload_file(directory_id=<directory_id>, file_path='<file_path>', description="<description(optional)>")
```

2. download file
```python
data.download_file(file_id=<file_id>, download_path="<place download file save> (default ./dsm.tmp)")
```
3. get file
```python
meta, file = get_file(file_id="<file_id>")
# meta -> dict
# file -> io bytes
```
```python
# example read csv pandas
 
meta, file = get_file(file_id="<file_id>")
df = pd.read_csv(file)
...
``` 

4. write parquet file
```python
df = ... # pandas dataframe or dask dataframe

data.write(df=df, directory=<directory_id>, name=<save_file_name>, profiling=<True or False default False>)
```

## Clickhouse
1. imoprt data to clickhouse

```python
from dsmlibrary.clickhouse import ClickHouse

ddf = ... # pandas dataframe or dask dataframe

## to warehouse
table_name = <your_table_name>
table_key = <your_table_key>

connection = { 
  'host': '', 
  'port': , 
  'database': '', 
  'user': '', 
  'password': '', 
  'settings':{ 
     'use_numpy': True 
  }, 
  'secure': False 
}

warehouse = ClickHouse(connection=connection)

tableName = warehouse.get_or_createTable(ddf=ddf, tableName=table_name, key=table_key)
warehouse.write(ddf=ddf, tableName=tableName, key=table_key)
```

2. query data from clickhouse
```python
query = f""" 
    SELECT * FROM {tableName} LIMIT 10 
""" 
warehouse.read(sqlQuery=query)

```