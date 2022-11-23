import pandas as pd
from pyarrow.parquet import ParquetFile
import pyarrow as pa 
from sqlalchemy import create_engine
from time import time
import os

def ingest_callable(user, password, host, port, db, table_name, url):

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    os.system(f"wget {url} -O output.parquet")

    pf = ParquetFile('output.parquet')

    for batch in pf.iter_batches(batch_size = 100000):
        t_start = time()
        
        df = pa.Table.from_batches([batch]).to_pandas()
        df.to_sql(name=table_name, con=engine, if_exists='append')
        
        t_end = time()
        
        print('inserted another chunk, took %.3f second' % (t_end - t_start))

