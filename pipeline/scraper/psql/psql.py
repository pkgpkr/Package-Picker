"""
Insert application, package, and dependency data into a PostgreSQL database
"""

import datetime
import os
import re
import psycopg2

INSERT_TO_APPLICATION_SQL = """
    INSERT INTO applications (url, name, followers, retrieved, hash)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT ON CONSTRAINT unique_url DO UPDATE
    SET (url, name, followers, retrieved, hash) = (EXCLUDED.url, EXCLUDED.name, EXCLUDED.followers, EXCLUDED.retrieved, EXCLUDED.hash)
    RETURNING id;
    """
INSERT_TO_PACKAGES_SQL = """
    INSERT INTO packages (name, retrieved)
    VALUES (%s, %s)
    ON CONFLICT(name) DO UPDATE
    SET (name, retrieved) = (EXCLUDED.name, EXCLUDED.retrieved)
    RETURNING id;
    """
UPDATE_PACKAGE_METADATA_SQL = """
    UPDATE packages SET
    downloads_last_month = %s,
    categories = %s,
    modified = %s
    WHERE name = %s;
    """
INSERT_TO_DEPENDENCIES_SQL = """
    INSERT INTO dependencies (application_id, package_id)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING;
    """

USER = os.environ.get('DB_USER') or "postgres"
PASSWORD = os.environ.get('DB_PASSWORD') or "secret"
HOST = os.environ.get('DB_HOST') or "localhost"
CONN_STRING = f"host={HOST} user={USER} password={PASSWORD}"

def connect_to_db():
    """
    Connect to the database
    """

    database = psycopg2.connect(CONN_STRING)
    return database


def insert_to_app(database, url, followers, app_name, app_hash):
    """
    Upsert a row into the applications table
    """

    cur = database.cursor()
    cur.execute(INSERT_TO_APPLICATION_SQL, (url,
                                            app_name,
                                            followers,
                                            datetime.datetime.now(),
                                            app_hash))
    application_id = cur.fetchone()[0]
    return application_id


def insert_to_package(database, name):
    """
    Upsert a row into the packages table
    """

    cur = database.cursor()
    cur.execute(INSERT_TO_PACKAGES_SQL, (name,
                                         datetime.datetime.now()))
    package_id = cur.fetchone()[0]
    return package_id

def update_package_metadata(database, name, downloads_last_month, categories, modified):
    """
    Update metadata for a particular package
    """

    # Reformat the category array to a string literal for PostgreSQL
    cur = database.cursor()
    category_string = None
    if categories and len(categories) > 0:

        # Remove any commas, curly braces, single quotes, and double quotes in the categories
        temp = [re.sub(r"[\,\{\}\'\"]", "", category) for category in categories]

        # Convert to an array literal for PostgreSQL
        category_string = str(temp).replace("'", "").replace("[", "{").replace("]", "}")

    cur.execute(UPDATE_PACKAGE_METADATA_SQL, (downloads_last_month,
                                              category_string,
                                              modified,
                                              name))

def insert_to_dependencies(database, application_id, package_id):
    """
    Upsert a row into the dependency table
    """

    cur = database.cursor()
    cur.execute(INSERT_TO_DEPENDENCIES_SQL, (application_id,
                                             package_id))
