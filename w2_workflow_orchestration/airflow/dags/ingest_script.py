import pandas as pd
from pyarrow.parquet import ParquetFile
import pyarrow as pa 
from sqlalchemy import create_engine
from time import time
import os
import platform

def ingest_callable(user, password, host, port, db, table_name, file, execution_date):
    print(table_name, file, execution_date)
    print(platform.python_version())
    print(pd.__version__)

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    print('connection established successfully, inserting data...')
    
    df = pd.read_parquet(file)
    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')

    pf = ParquetFile(file)

    for batch in pf.iter_batches(batch_size = 100000):
        t_start = time()
        
        df = pa.Table.from_batches([batch]).to_pandas()

        df.to_sql(name=table_name, con=engine, if_exists='append')
        
        t_end = time()
        
        print('inserted another chunk, took %.3f second' % (t_end - t_start))

