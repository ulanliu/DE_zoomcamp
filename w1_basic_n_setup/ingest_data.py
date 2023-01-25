import pandas as pd
import argparse
# from pyarrow.parquet import ParquetFile
# import pyarrow as pa 
from sqlalchemy import create_engine
from time import time
import os

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    file_name = 'green_taxi_2019.csv.gz'

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    os.system(f"wget {url} -O {file_name}")

    df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000)

    df = next(df_iter)

    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()

            df = next(df_iter)

            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()
            
            print("'inserted another chunk, took %.3f second' % (t_end - t_start)")

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break

    """ 
    if file is parquet file
    pf = ParquetFile(file_name) 

    for batch in pf.iter_batches(batch_size = 100000):
        t_start = time()
        
        df = pa.Table.from_batches([batch]).to_pandas()
        df.to_sql(name=table_name, con=engine, if_exists='append')
        
        t_end = time()
        
        print('inserted another chunk, took %.3f second' % (t_end - t_start))
    """
    
    os.system("wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv -O taxi_zone_lookup.csv")

    df_lookup = pd.read_csv('taxi_zone_lookup.csv')
    df_lookup.to_sql(name='taxi_zone_lookup', con=engine, if_exists='replace')
    
    print('successfully added')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest parquet data to Postgres')
    
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='db name for postgres')
    parser.add_argument('--table_name', help='name of the table where we will write the results to')
    parser.add_argument('--url', help='url for the file')

    args = parser.parse_args()

    main(args)