import psycopg2
import datetime
import os

INSERT_TO_APPLICATION_SQL = "INSERT INTO applications (url, name, followers, retrieved, hash) VALUES (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT unique_url DO UPDATE SET (url, name, followers, retrieved, hash) = (EXCLUDED.url, EXCLUDED.name, EXCLUDED.followers, EXCLUDED.retrieved, EXCLUDED.hash) RETURNING id;"
INSERT_TO_PACKAGES_SQL = "INSERT INTO packages (name, downloads_last_month, categories, modified, retrieved) VALUES (%s, %s, %s, %s, %s) ON CONFLICT(name) DO UPDATE SET (name, downloads_last_month, categories, modified) = (EXCLUDED.name, EXCLUDED.downloads_last_month, EXCLUDED.categories, EXCLUDED.modified) RETURNING id;"
INSERT_TO_DEPENDENCIES_SQL = "INSERT INTO dependencies (application_id, package_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;"

user = os.environ['DB_USER'] or "postgres"
password = os.environ['DB_PASSWORD'] or "secret"
host = os.environ['DB_HOST'] or "localhost"
conn_string = f"host={host} user={user} password={password}"

def connectToDB():

    # Connect to the database
    db = psycopg2.connect(conn_string)
    return db


def insertToApplication(db, url, followers, appName, hash):

    # Upsert a row into the applications table
    cur = db.cursor()
    cur.execute(INSERT_TO_APPLICATION_SQL, (url, appName, followers, datetime.datetime.now(), hash))
    application_id = cur.fetchone()[0]
    return application_id


def insertToPackages(db, name, downloads_last_month, categories, modified):

    # Reformat the category array to a string literal for PostgreSQL
    cur = db.cursor()
    categoryString = None
    if categories and len(categories) > 0:

        # Remove any commas in the categories
        temp = [category.replace(",", "") for category in categories]

        # Convert to an array literal for PostgreSQL
        categoryString = str(temp).replace("'", "").replace("[", "{").replace("]", "}")

    cur.execute(INSERT_TO_PACKAGES_SQL, (name, downloads_last_month, categoryString, modified, datetime.datetime.now()))
    package_id = cur.fetchone()[0]
    return package_id


def insertToDependencies(db, application_id, package_id):
    cur = db.cursor()
    cur.execute(INSERT_TO_DEPENDENCIES_SQL, (application_id, package_id))
