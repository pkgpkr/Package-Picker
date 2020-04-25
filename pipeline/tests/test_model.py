"""
Tests for the pipeline model
"""

import os
import unittest
import psycopg2

class TestScraper(unittest.TestCase):
    """
    Tests for the ML pipeline model
    """

    def setUp(self):

        # Connect to the database
        USER = os.environ.get('DB_USER')
        PASSWORD = os.environ.get('DB_PASSWORD')
        HOST = os.environ.get('DB_HOST')
        DATABASE = os.environ.get('DB_DATABASE')
        PORT = os.environ.get('DB_PORT')
        CONN_STRING = f"host={HOST} user={USER} password={PASSWORD} dbname={DATABASE} port={PORT}"
        self.database = psycopg2.connect(CONN_STRING)
        self.cursor = self.database.cursor()

        # TBD: Populate with data

    def tearDown(self):

        # TBD: Clean out all data
        
        self.cursor.close()
        self.database.close()

    def test_update_bounded_similarity_scores(self):
        pass

    def test_update_popularity_scores(self):
        pass

    def test_update_trending_scores(self):
        pass

    def test_package_table_postprocessing(self):
        pass