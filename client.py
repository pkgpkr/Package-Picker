import psycopg2
import os
import sys
sys.path.append('./pipeline/scraper')
import test

try: 
    user = 'postgres'
    password = 'postgres'
    database = 'postgres'
    real_token = os.environ['TOKEN']
    host = 'localhost'
    connection = None
    result = None
    connection = psycopg2.connect(user = user,
                                  password = password,
                                  host = host,
                                  port = 5432,
                                  database = database)
    cursor = connection.cursor()
    applications_table = """
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

    packages_table = """
        CREATE TABLE packages (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            downloads_last_month INTEGER,
            categories TEXT[],
            modified TIMESTAMPTZ,
            retrieved TIMESTAMPTZ NOT NULL
        );
    """

    dependencies_table = """
        CREATE TABLE dependencies (
            application_id INTEGER REFERENCES applications (id),
            package_id INTEGER REFERENCES packages (id),
            CONSTRAINT unique_app_to_pkg UNIQUE (application_id, package_id)
        );
    """
    cursor.execute(applications_table)
    cursor.execute(packages_table)
    cursor.execute(dependencies_table)
    connection.commit()  
    result = os.system("cd pipeline && pwd && DB_USER=%s DB_PASSWORD=%s DB_HOST=%s TOKEN=%s python3 -m unittest scraper/test.py -v" % (user,password,host,real_token))
     
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    if (result == None):
        raise Exception("Database cannot be created!")
    elif (result != 0):
        raise Exception("Test failed!")
    
