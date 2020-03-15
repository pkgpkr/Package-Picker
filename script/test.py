# This is used to test PSQL, ignore this
#!/usr/bin/python
import psycopg2
import sys
import PSQL
 
def main():
    db = PSQL.connectToDB()
    cur = db.cursor()
    cur.execute("SELECT * FROM applications;")
    result = cur.fetchall()
    print(result)

if __name__ == "__main__":
    main()