import psycopg2
import pandas as pd

def get_pg_data(db, query, limit=None):
    conn = psycopg2.connect(
        dbname=db,
        user="postgres",
        password="MPpm@123",
        host="localhost",
        port="5432"
    )

    if limit:
        query += f" LIMIT {limit}"

    df = pd.read_sql(query, conn)
    conn.close()
    return df
