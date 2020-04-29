"""
Train the model and do post-processing on the database
"""

import os
import psycopg2
from model import model
from model import database

def main():

    # Connect to the database
    USER = os.environ.get('DB_USER')
    PASSWORD = os.environ.get('DB_PASSWORD')
    HOST = os.environ.get('DB_HOST')
    DATABASE = os.environ.get('DB_DATABASE')
    PORT = os.environ.get('DB_PORT')
    CONN_STRING = f"host={HOST} user={USER} password={PASSWORD} dbname={DATABASE} port={PORT}"

    # Assert that the necessary environment variables are present
    assert USER, "DB_USER not set"
    assert PASSWORD, "DB_PASSWORD not set"
    assert HOST, "DB_HOST not set"
    assert DATABASE, "DB_DATABASE not set"
    assert PORT, "DB_PORT not set"

    # Connect to the database
    db_handle = psycopg2.connect(CONN_STRING)
    cursor = db_handle.cursor()

    # ML pipeline
    scores = model.get_similarity_dataframe(cursor)
    database.write_similarity_scores(scores, HOST, PORT, DATABASE, "similarity", USER, PASSWORD)
    database.update_bounded_similarity_scores(cursor)
    database.update_popularity_scores(cursor)
    database.update_trending_scores(cursor)
    database.package_table_postprocessing(cursor)

    # Commit changes and close the database connection
    db_handle.commit()
    cursor.close()
    db_handle.close()

if __name__ == "__main__":
   main()
