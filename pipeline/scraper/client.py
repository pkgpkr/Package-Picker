"""
Provision a new database before running scraper tests
"""

import os
import psycopg2

try:
    USER = 'postgres'
    PASSWORD = 'postgres'
    DATABASE = 'postgres'
    REAL_TOKEN = os.environ['TOKEN']
    HOST = 'localhost'
    CONNECTION = None
    RESULT = None
    CONNECTION = psycopg2.connect(user=USER,
                                  password=PASSWORD,
                                  host=HOST,
                                  port=5432,
                                  database=DATABASE)
    CURSOR = CONNECTION.cursor()
    APPLICATIONS_TABLE = """
        CREATE TABLE applications (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            name TEXT NOT NULL,
            followers INTEGER,
            hash TEXT NOT NULL,
            retrieved TIMESTAMPTZ NOT NULL,
            CONSTRAINT unique_url UNIQUE (url)
        );
    """

    PACKAGES_TABLE = """
        CREATE TABLE packages (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            downloads_last_month INTEGER,
            categories TEXT[],
            modified TIMESTAMPTZ,
            retrieved TIMESTAMPTZ NOT NULL
        );
    """

    DEPENDENCIES_TABLE = """
        CREATE TABLE dependencies (
            application_id INTEGER REFERENCES applications (id),
            package_id INTEGER REFERENCES packages (id),
            CONSTRAINT unique_app_to_pkg UNIQUE (application_id, package_id)
        );
    """
    CURSOR.execute(APPLICATIONS_TABLE)
    CURSOR.execute(PACKAGES_TABLE)
    CURSOR.execute(DEPENDENCIES_TABLE)
    CONNECTION.commit()
    RESULT = os.system(f"""
DB_USER={USER} \
DB_PASSWORD={PASSWORD} \
DB_HOST={HOST} \
TOKEN={REAL_TOKEN} \
python3 -m unittest test.py -v
                       """)

except psycopg2.Error as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if CONNECTION:
        CURSOR.close()
        CONNECTION.close()
        print("PostgreSQL connection is closed")
    if RESULT is None:
        raise Exception("Database cannot be created!")
    if RESULT != 0:
        raise Exception("Test failed!")
