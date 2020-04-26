"""
Provision a new database before running scraper tests
"""

import os
import psycopg2

try:
    USER = os.environ['DB_USER']
    PASSWORD = os.environ['DB_PASSWORD']
    DATABASE = os.environ['DB_DATABASE']
    REAL_TOKEN = os.environ['GH_TOKEN']
    HOST = os.environ['DB_HOST']
    PORT = os.environ['DB_PORT']
    CONNECTION = None
    RESULT = None
    CONNECTION = psycopg2.connect(user=USER,
                                  password=PASSWORD,
                                  host=HOST,
                                  port=PORT,
                                  database=DATABASE)
    with CONNECTION.cursor() as cursor:
      cursor.execute(open("provision_db.sql", "r").read())
    RESULT = os.system(f"""
DB_USER={USER} \
DB_PASSWORD={PASSWORD} \
DB_HOST={HOST} \
DB_PORT={PORT} \
DB_DATABASE={DATABASE} \
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
