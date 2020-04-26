"""
Provision a new database before running scraper tests
"""

import os
import psycopg2

try:
    USER = 'postgres'
    PASSWORD = 'postgres'
    DATABASE = 'postgres'
    REAL_TOKEN = os.environ['GITHUB_TOKEN']
    HOST = 'localhost'
    CONNECTION = None
    RESULT = None
    CONNECTION = psycopg2.connect(user=USER,
                                  password=PASSWORD,
                                  host=HOST,
                                  port=5432,
                                  database=DATABASE)
    with CONNECTION.cursor() as cursor:
      cursor.execute(open("provision_db.sql", "r").read())
    RESULT = os.system(f"""
DB_USER={USER} \
DB_PASSWORD={PASSWORD} \
DB_HOST={HOST} \
GH_TOKEN={REAL_TOKEN} \
python3 -m unittest -v
                       """)

except psycopg2.Error as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if CONNECTION:
        CONNECTION.close()
        print("PostgreSQL connection is closed")
    if RESULT is None:
        raise Exception("Database cannot be created!")
    if RESULT != 0:
        raise Exception("Test failed!")
