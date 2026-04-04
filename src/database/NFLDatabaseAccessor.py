import configparser
import os
import pandas as pd
import psycopg
import pandas.io.sql as psql
import os
import yaml
import json

from pathlib import Path

from ..utils import get_root

class DatabaseAccessor:
    def __init__(self):
        self.data_path = Path(os.getcwd(), "data")

        config = configparser.ConfigParser()
        config.read(Path(self.data_path, "config.ini"))

        config = json.load(open(Path(get_root(), "config.json")))

        host = config['Database']['host']
        port = config['Database']['port']
        dbname = config['Database']['dbname']
        user = config['Database']['user']
        connect_timeout = config['Database']['connect_timeout']
        sslmode = config['Database']['sslmode']
        password = config['Database']['password']
        self.connection = psycopg.connect(f"host={host} port={port} dbname={dbname} user={user} connect_timeout={connect_timeout} sslmode={sslmode} password={password}")

    def create_table(self, table: str, schema: str, primary_index : str = None, foreign_keys : dict[str,str] = None) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({schema});")
            if primary_index != None:
                cursor.execute(f"CREATE UNIQUE INDEX {table}_primary_key_index on {table} {primary_index}")
            if foreign_keys != None:
                for key, ref in foreign_keys.items():
                    cursor.execute(f"ALTER TABLE {table} ADD CONSTRAINT fk_{key} FOREIGN KEY ({key}) REFERENCES {ref};")
            self.connection.commit()

    def create_type(self, type_name: str, values: list[str]) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{type_name}') THEN CREATE TYPE {type_name} AS ENUM ({', '.join([f'\'{val}\'' for val in values])}); END IF; END $$;")
            self.connection.commit()

    def drop_table(self, table:str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            self.connection.commit() 

    def write_data(self, table : str, id : str, dataframe: pd.DataFrame):
        with self.connection.cursor() as cursor:
            for _, row in dataframe.iterrows():
                columns = ", ".join(row.index.tolist())
                values = ", ".join([f"'{str(val).replace("'","")}'" for val in row.values])
                values = values.replace('\'None\'','NULL')
                sql = f"INSERT INTO {table} ({columns}) VALUES ({values}) ON CONFLICT ({id}) DO UPDATE SET {','.join([' = '.join(x) for x in zip(columns.split(','), values.split(','))])};"
                cursor.execute(sql)
            self.connection.commit()

    def read_data(self, query: str) -> pd.DataFrame:
        return psql.read_sql(query, self.connection)

    def check_table_exists(self, table: str) -> bool:
         with self.connection.cursor() as cursor:
            query = f"SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}');"
            result = cursor.execute(query)
            return bool(cursor.fetchall()[0][0])
         
    def close(self):
        self.connection.close()