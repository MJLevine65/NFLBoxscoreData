import pandas as pd
import psycopg
from pathlib import Path
import os

class DatabaseAccessor:
    def __init__(self):
        self.data_path = Path(os.getcwd(), "data")
        self.connection = psycopg.connect("host=localhost port=5432 dbname=NFLDatabase user=postgres connect_timeout=10 sslmode=prefer password=6567")

    def create_table(self, table: str, schema: str, primary_index : str = None) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({schema});")
            if primary_index != None:
                cursor.execute(f"CREATE UNIQUE INDEX {table}_primary_key_index on {table} {primary_index}")
            self.connection.commit()

    def drop_table(self, table:str) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table} ")
            self.connection.commit() 

    # def clear_data(self, table: str) -> None:
    #     with self.connection.cursor() as cursor:
    #         cursor.execute(f"TRUNCATE TABLE {table} IF EXISTS {table};")
    #         self.connection.commit()

    def write_data(self, table : str, id : str, dataframe: pd.DataFrame):
        with self.connection.cursor() as cursor:
            for _, row in dataframe.iterrows():
                columns = ", ".join(row.index.tolist())
                values = ", ".join([f"'{str(val).replace("'","")}'" for val in row.values])
                values = values.replace('\'None\'','NULL')
                sql = f"INSERT INTO {table} ({columns}) VALUES ({values}) ON CONFLICT ({id}) DO UPDATE SET {','.join([' = '.join(x) for x in zip(columns.split(','), values.split(','))])};"
                cursor.execute(sql)
            self.connection.commit()

    def read_schema(self, dataframe : pd.DataFrame) -> str:
        columns = []
        for col, dtype in zip(dataframe.columns, dataframe.dtypes):
            if dtype == 'int64':
                sql_type = "INT"
            elif dtype == 'float64':
                sql_type = "FLOAT"
            else:
                sql_type = "VARCHAR(255)"
            columns.append(f"{col} {sql_type}")
        return ", ".join(columns)

    def check_table_exists(self, table: str, cursor) -> bool:
        query = f"SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}');"
        result = cursor.execute(query)
        return bool(result)