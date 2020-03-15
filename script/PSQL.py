import psycopg2
import datetime

# user = "postgres"
# password = "sL6IpcVZKv57HcZZTX3x"
# host = "package-picker-test.c7etfrntf9yq.us-east-1.rds.amazonaws.com"

conn_string = "host='localhost' dbname='postgres' user='postgres' password='secret'"
def connectToDB():
    # Connect to the database
    db = psycopg2.connect(conn_string)
    return db

def insertToApplication(db, url, followers, appName):
    # Get a cursor for executing queries
    cur = db.cursor()
    # Upsert a row into the applications table
    cur.execute("INSERT INTO applications (url, name, followers, retrieved) VALUES (%s, %s, %s, %s) ON CONFLICT ON CONSTRAINT unique_url_and_hash DO UPDATE SET (url, name, followers, retrieved) = (EXCLUDED.url, EXCLUDED.name, EXCLUDED.followers, EXCLUDED.retrieved)", (url, appName, followers, datetime.datetime.now()))
    print("%s, %s, %s", (url, appName, followers))
    # Commit the transaction
    db.commit()
    # Get the row you just inserted
    cur.execute("SELECT * FROM applications;")
    return cur.fetchall()

