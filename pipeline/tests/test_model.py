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

        # Package data
        package_data = [
            {
                'id': 1,
                'name': '\'pkg:npm/countup.js@2\'',
                'monthly_downloads_last_month': 400451,
                'monthly_downloads_a_year_ago': 203833,
                'categories': 'null',
                'modified': '\'2019-03-14 12:42:34.846-07\'',
                'retrieved': '\'2020-04-25 19:03:37.409069-07\''
            },
            {
                'id': 2,
                'name': '\'pkg:npm/d3@5\'',
                'monthly_downloads_last_month': 5306004,
                'monthly_downloads_a_year_ago': 2966818,
                'categories': '\'{dom,visualization,svg,animation,canvas}\'',
                'modified': '\'2020-04-20 10:59:10.332-07\'',
                'retrieved': '\'2020-04-25 19:03:37.421523-07\''
            },
            {
                'id': 4,
                'name': '\'pkg:npm/globe.gl@2\'',
                'monthly_downloads_last_month': 2221,
                'monthly_downloads_a_year_ago': 771,
                'categories': '\'{webgl,three,globe,geo,spherical,projection,orthographic}\'',
                'modified': '\'2020-04-10 14:13:59.518-07\'',
                'retrieved': '\'2020-04-25 19:03:37.426579-07\''
            },
            {
                'id': 5,
                'name': '\'pkg:npm/react-resize-detector@4\'',
                'monthly_downloads_last_month': 2875528,
                'monthly_downloads_a_year_ago': 1957316,
                'categories': '\'{react,resize,detector}\'',
                'modified': '\'2020-04-15 00:39:01.617-07\'',
                'retrieved': '\'2020-04-25 19:03:37.429703-07\''
            },
            {
                'id': 8,
                'name': '\'pkg:npm/@reach/router@1\'',
                'monthly_downloads_last_month': 0,
                'monthly_downloads_a_year_ago': 0,
                'categories': '\'{react,"react router"}\'',
                'modified': '\'2020-02-27 12:14:25.729-08\'',
                'retrieved': '\'2020-04-25 19:03:37.434285-07\''
            }
        ]

        # Connect to the database
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASSWORD')
        host = os.environ.get('DB_HOST')
        database = os.environ.get('DB_DATABASE')
        port = os.environ.get('DB_PORT')
        connection_string = f"host={host} user={user} password={password} dbname={database} port={port}"
        self.database = psycopg2.connect(connection_string)
        self.cursor = self.database.cursor()

        # Populate with package data
        for p in package_data:
            self.cursor.execute(f"""
            INSERT INTO packages (id, name, monthly_downloads_last_month, monthly_downloads_a_year_ago, categories, modified, retrieved )
            VALUES ({p['id']}, {p['name']}, {p['monthly_downloads_last_month']}, {p['monthly_downloads_a_year_ago']}, {p['categories']}, {p['modified']}, {p['retrieved']});""")
        
        # Commit changes
        self.database.commit()

    def tearDown(self):

        # Clean out all data
        self.cursor.execute("DELETE FROM dependencies; DELETE FROM similarity; DELETE FROM applications; DELETE FROM packages;")
        self.database.commit()
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