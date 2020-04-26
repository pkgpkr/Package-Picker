"""
Tests for the pipeline model
"""

import os
import unittest
import psycopg2
from model.model import update_bounded_similarity_scores, update_popularity_scores, update_trending_scores, package_table_postprocessing

class TestModel(unittest.TestCase):
    """
    Tests for the ML pipeline model
    """

    def setUp(self):

        # Application data
        app_data = [
            1,
            2
        ]

        # Package data
        package_data = [
            {
                'id': 1,
                'name': '\'pkg:npm/countup.js@2\'',
                'monthly_downloads_last_month': 400451,
                'monthly_downloads_a_year_ago': 0,
                'categories': 'null',
                'modified': '\'2019-03-14 12:42:34.846-07\'',
                'retrieved': '\'2020-04-25 19:03:37.409069-07\'',
                'app_ids': app_data[-1:]
            },
            {
                'id': 2,
                'name': '\'pkg:npm/d3@5\'',
                'monthly_downloads_last_month': 5306004,
                'monthly_downloads_a_year_ago': 2966818,
                'categories': '\'{dom,visualization,svg,animation,canvas}\'',
                'modified': '\'2020-04-20 10:59:10.332-07\'',
                'retrieved': '\'2020-04-25 19:03:37.421523-07\'',
                'app_ids': app_data
            },
            {
                'id': 4,
                'name': '\'pkg:npm/globe.gl@2\'',
                'monthly_downloads_last_month': 2221,
                'monthly_downloads_a_year_ago': 771,
                'categories': '\'{webgl,three,globe,geo,spherical,projection,orthographic}\'',
                'modified': '\'2020-04-10 14:13:59.518-07\'',
                'retrieved': '\'2020-04-25 19:03:37.426579-07\'',
                'app_ids': app_data
            },
            {
                'id': 5,
                'name': '\'pkg:npm/react-resize-detector@4\'',
                'monthly_downloads_last_month': 0,
                'monthly_downloads_a_year_ago': 1957316,
                'categories': '\'{react,resize,detector}\'',
                'modified': 'null',
                'retrieved': '\'2020-04-25 19:03:37.429703-07\'',
                'app_ids': app_data
            },
            {
                'id': 8,
                'name': '\'pkg:npm/@reach/router@1\'',
                'monthly_downloads_last_month': 0,
                'monthly_downloads_a_year_ago': 0,
                'categories': '\'{react,"react router"}\'',
                'modified': '\'2020-02-27 12:14:25.729-08\'',
                'retrieved': '\'2020-04-25 19:03:37.434285-07\'',
                'app_ids': app_data[:1]
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
            VALUES ({p['id']}, {p['name']}, {p['monthly_downloads_last_month']}, {p['monthly_downloads_a_year_ago']}, {p['categories']}, {p['modified']}, {p['retrieved']});
            """)
        
        # Populate with similarity data
        for p1 in package_data:
            for p2 in package_data:
                if p1['id'] == p2['id']:
                    continue

                # Determine how much overlap the two packages have
                similarity = len(set(p1['app_ids']) & set(p2['app_ids'])) / len(set(p1['app_ids']) | set(p2['app_ids']))
                if similarity == 0:
                    continue

                # Insert similarity score into database
                self.cursor.execute(f"""
                INSERT INTO similarity (package_a, package_b, similarity)
                VALUES ({p1['id']}, {p2['id']}, {similarity});
                """)

    def tearDown(self):

        # Clean out all data
        self.cursor.execute("DELETE FROM dependencies; DELETE FROM similarity; DELETE FROM applications; DELETE FROM packages;")
        self.database.commit()
        self.cursor.close()
        self.database.close()

    def test_update_bounded_similarity_scores(self):
        update_bounded_similarity_scores(self.cursor)
        self.cursor.execute("SELECT bounded_similarity FROM similarity ORDER BY package_a, package_b;")
        scores = self.cursor.fetchall()
        self.assertListEqual(scores, [
                                        (5,), (5, ), (5, ),        # Package 1
                                        (5,), (10,), (10,), (5,),  # Package 2
                                        (5,), (10,), (10,), (5,),  # Package 4
                                        (5,), (10,), (10,), (5,),  # Package 5
                                              (5, ), (5, ), (5,)]) # Package 8

    def test_update_popularity_scores(self):
        update_popularity_scores(self.cursor)
        self.cursor.execute("SELECT bounded_popularity FROM packages ORDER BY id;")
        scores = self.cursor.fetchall()
        self.assertListEqual(scores, [(8,), (10,), (10,), (10,), (8,)])

    def test_update_trending_scores(self):
        update_trending_scores(self.cursor)

        # Check absolute trend
        self.cursor.execute("SELECT absolute_trend FROM packages ORDER by id;")
        scores = self.cursor.fetchall()
        self.assertListEqual(scores, [(10,), (5,), (6,), (1,), (5,)])

        # Check relative trend
        self.cursor.execute("SELECT relative_trend FROM packages ORDER BY id;")
        scores = self.cursor.fetchall()
        self.assertListEqual(scores, [(10,), (2,), (2,), (1,), (1,)])

    def test_package_table_postprocessing(self):
        package_table_postprocessing(self.cursor)
        self.cursor.execute("SELECT short_name, url, display_date FROM packages ORDER BY id;")
        metadata = self.cursor.fetchall()
        self.assertEqual(metadata[0], ('countup.js@2', 'https://npmjs.com/package/countup.js', '2019-03-14'))
        self.assertEqual(metadata[1], ('d3@5', 'https://npmjs.com/package/d3', '2020-04-20'))
        self.assertEqual(metadata[2], ('globe.gl@2', 'https://npmjs.com/package/globe.gl', '2020-04-10'))
        self.assertEqual(metadata[3], ('react-resize-detector@4', 'https://npmjs.com/package/react-resize-detector', None))
        self.assertEqual(metadata[4], ('@reach/router@1', 'https://npmjs.com/package/@reach/router', '2020-02-27'))
