import psycopg2
import datetime
import os
import re

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

user = os.environ.get('DB_USER', default="postgres")
password = os.environ.get('DB_PASSWORD', default=None)
host = os.environ.get('DB_HOST', default="localhost")
conn_string = f"host={host} user={user}"
if password:
    conn_string += f" password={password}"

def connectToDB():

    # Connect to the database
    db = psycopg2.connect(conn_string)
    return db


def insertToApplication(db, url, followers, appName, hash):

    # Upsert a row into the applications table
    cur = db.cursor()
    cur.execute(INSERT_TO_APPLICATION_SQL, (url, appName, followers, datetime.datetime.now(), hash))
    application_id = cur.fetchone()[0]
    db.commit()
    return application_id


def insertToPackages(db, name):

    # Upsert a row into the packages table
    cur = db.cursor()
    cur.execute(INSERT_TO_PACKAGES_SQL, (name, datetime.datetime.now()))
    package_id = cur.fetchone()[0]
    db.commit()
    return package_id

def updatePackageMetadata(db, name, downloads_last_month, categories, modified):

    # Reformat the category array to a string literal for PostgreSQL
    cur = db.cursor()
    categoryString = None
    if categories and len(categories) > 0:

        # Remove any commas, curly braces, single quotes, and double quotes in the categories
        temp = [re.sub(r"[\,\{\}\'\"]", "", category) for category in categories]

        # Convert to an array literal for PostgreSQL
        categoryString = str(temp).replace("'", "").replace("[", "{").replace("]", "}")

    # Update package metadata
    cur.execute(UPDATE_PACKAGE_METADATA_SQL, (downloads_last_month, categoryString, modified, name))
    db.commit()

def insertToDependencies(db, application_id, package_id):
    cur = db.cursor()
    cur.execute(INSERT_TO_DEPENDENCIES_SQL, (application_id, package_id))
    db.commit()
