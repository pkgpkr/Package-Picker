import psycopg2
import datetime
import os

user = os.environ['DB_USER'] or "postgres"
password = os.environ['DB_PASSWORD'] or "secret"
host = os.environ['DB_HOST'] or "localhost"
conn_string = f"host={host} user={user} password={password}"

def connectToDB():
    # Connect to the database
    db = psycopg2.connect(conn_string)
    return db


def insertToApplication(db, url, followers, appName, hash):
    # Get a cursor for executing queries
    cur = db.cursor()
    # Upsert a row into the applications table
    cur.execute(
        "INSERT INTO applications (url, name, followers, retrieved, hash) VALUES (%s, %s, %s, %s, %s) ON CONFLICT ON CONSTRAINT unique_url_and_hash DO UPDATE SET (url, name, followers, retrieved, hash) = (EXCLUDED.url, EXCLUDED.name, EXCLUDED.followers, EXCLUDED.retrieved, EXCLUDED.hash) RETURNING id;",
        (url, appName, followers, datetime.datetime.now(), hash))
    application_id = cur.fetchone()[0]
    return application_id


def insertToPackages(db, name):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO packages (name, retrieved) VALUES (%s, %s) ON CONFLICT(name) DO UPDATE SET name=EXCLUDED.name RETURNING id;",
        (name, datetime.datetime.now()))
    package_id = cur.fetchone()[0]
    return package_id


def insertToDependencies(db, application_id, package_id):
    cur = db.cursor()
    cur.execute("INSERT INTO dependencies (application_id, package_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (application_id, package_id))
