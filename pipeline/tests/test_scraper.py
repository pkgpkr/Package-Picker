"""
Test script for the ML pipeline scraper
"""

import os
import unittest
import datetime
import psycopg2
from scraper.month_calculation import month_delta
from scraper.psql import connect_to_db, insert_to_app, insert_to_dependencies, insert_to_package, update_package_metadata
from scraper import github
from scraper import pypi

assert os.environ.get('GH_TOKEN'), "GH_TOKEN not set"

class TestScraper(unittest.TestCase):
    """
    Tests for the ML pipeline scraper
    """
    @classmethod
    def setUpClass(cls):

        USER = os.environ['DB_USER']
        PASSWORD = os.environ['DB_PASSWORD']
        DATABASE = os.environ['DB_DATABASE']
        REAL_TOKEN = os.environ['GH_TOKEN']
        HOST = os.environ['DB_HOST']
        PORT = os.environ['DB_PORT']
        connection = None
        result = None
        cls.connection = psycopg2.connect(user=USER,
                                      password=PASSWORD,
                                      host=HOST,
                                      port=PORT,
                                      database=DATABASE)
        f = open("tests/provision_db.sql", "r")
        cls.connection.cursor().execute(f.read())
        cls.connection.commit()
        f.close()


    def tearDown(self):

        # Connect to the database
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASSWORD')
        host = os.environ.get('DB_HOST')
        database = os.environ.get('DB_DATABASE')
        port = os.environ.get('DB_PORT')
        connection_string = f"host={host} user={user} password={password} dbname={database} port={port}"
        database = psycopg2.connect(connection_string)
        cursor = database.cursor()

        # Clean out all data
        cursor.execute("DELETE FROM dependencies; DELETE FROM similarity; DELETE FROM applications; DELETE FROM packages;")
        database.commit()
        cursor.close()
        database.close()

    def test_month_delta(self):
        """
        Try to calculate month offsets from a given date
        """

        # Test no offset
        november = datetime.date(2018, 10, 31)
        self.assertEqual(month_delta(november, 0), datetime.date(2018, 10, 31))

        # Test one offset
        self.assertEqual(month_delta(november, 1), datetime.date(2018, 9, 30))

        # Test 12 offset
        self.assertEqual(month_delta(november, 12), datetime.date(2017, 10, 31))

        # Test 60 offset
        self.assertEqual(month_delta(november, 60), datetime.date(2013, 10, 31))

        # Test leap year
        self.assertEqual(month_delta(november, 224), datetime.date(2000, 2, 29))

        # Test non-leap year
        self.assertEqual(month_delta(november, 8), datetime.date(2018, 2, 28))


    def test_run_query(self):
        """
        Try fetching a month of data from the GitHub API
        """

        distant_past = datetime.date(2011, 1, 1)
        github.run_query(distant_past)


    def test_run_query_once(self):
        """
        Try fetching data from the GitHub API
        """

        month_str = "created:2020-01-01..2020-02-01"
        cursor = None
        for i in [1, 10, 100]:
            try:
                result = github.run_query_once(i, month_str, cursor, "JavaScript")
                self.assertIsNotNone(result['data']['search']['edges'])
                result = None
                result = github.run_query_once(i, month_str, cursor, "Python")
                self.assertIsNotNone(result['data']['search']['edges'])
            except ValueError:
                self.assertIsNone(result)

    def test_connect_to_db(self):
        """
        Try connecting to the database
        """

        database = connect_to_db()
        self.assertIsNotNone(database)


    def test_insert_to_application(self):
        """
        Try inserting an application into the application table
        """

        database = connect_to_db()
        url = "www.pkgpkr.com"
        followers = 314
        app_name = "pkgpkr"
        my_hash = hash(app_name)
        app_id = insert_to_app(database, url, followers, app_name, my_hash)
        self.assertIsInstance(app_id, int)
        cur = database.cursor()
        cur.execute(
            f"SELECT name FROM applications WHERE id = { app_id };"
        )
        application_name = cur.fetchone()[0]
        self.assertEqual(application_name, app_name)


    def test_insert_to_packages(self):
        """
        Try inserting a package into the package table
        """

        database = connect_to_db()
        name = "myPkg"
        package_id = insert_to_package(database, name)
        self.assertIsInstance(package_id, int)
        cur = database.cursor()
        cur.execute(
            f"SELECT name FROM packages WHERE id = { package_id };"
        )
        package_name = cur.fetchone()[0]
        self.assertEqual(package_name, name)


    def test_update_package_metadata(self):
        """
        Try to update the metadata associated with a package
        """

        database = connect_to_db()
        name = "myPkg"
        downloads_last_month = 200
        categories = ["critical", ",,comma", "\\{braces\\}", "\'quoted\""]
        modified = datetime.datetime.now()

        # Insert package into the table
        package_id = insert_to_package(database, name)
        self.assertIsInstance(package_id, int)

        # Ensure that the modified field is None
        cur = database.cursor()
        cur.execute(
            f"SELECT modified FROM packages WHERE id = { package_id };"
        )
        modified_date = cur.fetchone()[0]
        self.assertIsNone(modified_date)

        # Update metadata in the table
        update_package_metadata(database, name, downloads_last_month, downloads_last_month, categories, modified)

        # Ensure that the modified field is now not None
        cur.execute(
            f"SELECT modified FROM packages WHERE id = { package_id };"
        )
        modified_date = cur.fetchone()[0]
        self.assertIsNotNone(modified_date)

        # Upsert the same package into the table again
        package_id = insert_to_package(database, name)
        self.assertIsInstance(package_id, int)

        # Ensure that the modified field is still not None
        cur.execute(
            f"SELECT modified FROM packages WHERE id = { package_id };"
        )
        modified_date = cur.fetchone()[0]
        self.assertIsNotNone(modified_date)


    def test_insert_to_dependencies(self):
        """
        Try to insert a dependency into the dependency table
        """

        database = connect_to_db()
        url = "www.pkgpkr.com"
        followers = 314
        app_name = "pkgpkr"
        my_hash = hash(app_name)
        application_id = insert_to_app(database, url, followers, app_name, my_hash)
        name = "myPkg"
        package_id = insert_to_package(database, name)
        insert_to_dependencies(database, application_id, package_id)
        cur = database.cursor()
        cur.execute(
            f"SELECT * FROM dependencies WHERE application_id = { application_id } AND package_id ={ package_id };"
        )
        result = cur.fetchall()
        self.assertEqual(result, [(application_id, package_id)])

    def test_get_package_metadata_pypi(self):
        """
        Try to update pypi metadata
        """

        dependency = 'pkg:pypi/django@2'
        entry = pypi.get_package_metadata(dependency)
        self.assertIsInstance(entry['monthly_downloads_last_month'], int)
        self.assertIsInstance(entry['monthly_downloads_a_year_ago'], int)
        self.assertIsInstance(entry['categories'], type(['Utilities', 'Internet']))
        self.assertIsInstance(entry['modified'], str)

    # def test_run_query_pypi(self):
    #     database = connect_to_db()
    #     cur = database.cursor()
    #     name = 'pkg:pypi/django@2'
    #     package_id = insert_to_package(database, name)
    #     self.assertIsInstance(package_id, int)
    #     pypi.run_query()

    #     database = connect_to_db()
    #     cur = database.cursor()
    #     cur.execute(
    #         f"SELECT monthly_downloads_last_month FROM packages WHERE name = '{ name }';"
    #     )
    #     monthly_downloads_last_month = cur.fetchone()[0]
    #     self.assertIsInstance(monthly_downloads_last_month, int)

    #     cur.execute(
    #         f"SELECT monthly_downloads_a_year_ago FROM packages WHERE name = '{ name }';"
    #     )
    #     monthly_downloads_a_year_ago = cur.fetchone()[0]
    #     self.assertIsInstance(monthly_downloads_a_year_ago, int)

    #     cur.execute(
    #         f"SELECT categories FROM packages WHERE name = '{ name }';"
    #     )
    #     categories = cur.fetchone()[0]
    #     self.assertIsInstance(categories, type(['Utilities', 'Internet']))

    #     cur.execute(
    #         f"SELECT modified FROM packages WHERE name = '{ name }';"
    #     )
    #     modified = cur.fetchone()[0]
    #     self.assertIsInstance(modified, str)

    def test_get_package_metadata_npm(self):
        """
        Try to update npm metadata
        """

        dependency = 'pkg:npm/react@2'
        entry = pypi.get_package_metadata(dependency)
        self.assertIsInstance(entry['monthly_downloads_last_month'], int)
        self.assertIsInstance(entry['monthly_downloads_a_year_ago'], int)
        self.assertIsInstance(entry['categories'], type(['Utilities', 'Internet']))
        self.assertIsInstance(entry['modified'], str)

    def test_run_query_npm(self):
        return

    @classmethod
    def tearDownClass(cls):
        #closing and cleaning up the test database
        if cls.connection:
            f = open("tests/deprovision_db.sql", "r")
            cls.connection.cursor().execute(f.read())
            cls.connection.commit()
            cls.connection.close()
            print("PostgreSQL connection is closed succesfully")
            f.close()
