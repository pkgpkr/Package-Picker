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
from scraper import npm

assert os.environ.get('GH_TOKEN'), "GH_TOKEN not set"

json_result_js = {
          "data": {
            "search": {
              "edges": [
                {
                  "node": {
                    "nameWithOwner": "wuhan2020/wuhan2020",
                    "url": "https://github.com/wuhan2020/wuhan2020",
                    "watchers": {
                      "totalCount": 255
                    },
                    "object": None
                  },
                  "cursor": "Y3Vyc29yOjE="
                },
                {
                  "node": {
                    "nameWithOwner": "excalidraw/excalidraw",
                    "url": "https://github.com/excalidraw/excalidraw",
                    "watchers": {
                      "totalCount": 99
                    },
                    "object": {
                      "text": "{\n  \"browserslist\": {\n    \"production\": [\n      \">0.2%\",\n      \"not dead\",\n      \"not ie <= 11\",\n      \"not op_mini all\",\n      \"not safari < 12\",\n      \"not kaios <= 2.5\",\n      \"not edge < 79\",\n      \"not chrome < 70\",\n      \"not and_uc < 13\",\n      \"not samsung < 10\"\n    ],\n    \"development\": [\n      \"last 1 chrome version\",\n      \"last 1 firefox version\",\n      \"last 1 safari version\"\n    ]\n  },\n  \"dependencies\": {\n    \"@sentry/browser\": \"5.15.5\",\n    \"@sentry/integrations\": \"5.15.5\",\n    \"browser-nativefs\": \"0.7.1\",\n    \"i18next-browser-languagedetector\": \"4.1.1\",\n    \"nanoid\": \"2.1.11\",\n    \"open-color\": \"1.7.0\",\n    \"points-on-curve\": \"0.2.0\",\n    \"pwacompat\": \"2.0.11\",\n    \"react\": \"16.13.1\",\n    \"react-dom\": \"16.13.1\",\n    \"react-scripts\": \"3.4.1\",\n    \"roughjs\": \"4.2.3\",\n    \"socket.io-client\": \"2.3.0\",\n    \"node-sass\": \"4.14.0\",\n    \"typescript\": \"3.8.3\",\n    \"@types/jest\": \"25.2.1\",\n    \"@types/nanoid\": \"2.1.0\",\n    \"@types/react\": \"16.9.34\",\n    \"@types/react-dom\": \"16.9.6\",\n    \"@types/socket.io-client\": \"1.4.32\",\n    \"@testing-library/jest-dom\": \"5.5.0\",\n    \"@testing-library/react\": \"10.0.3\"\n  },\n  \"devDependencies\": {\n    \"asar\": \"3.0.3\",\n    \"eslint\": \"6.8.0\",\n    \"eslint-config-prettier\": \"6.11.0\",\n    \"eslint-plugin-prettier\": \"3.1.3\",\n    \"husky\": \"4.2.5\",\n    \"jest-canvas-mock\": \"2.2.0\",\n    \"lint-staged\": \"10.1.7\",\n    \"pepjs\": \"0.5.2\",\n    \"prettier\": \"2.0.5\",\n    \"rewire\": \"5.0.0\"\n  },\n  \"engines\": {\n    \"node\": \">=12.0.0\"\n  },\n  \"homepage\": \".\",\n  \"husky\": {\n    \"hooks\": {\n      \"pre-commit\": \"lint-staged\"\n    }\n  },\n  \"jest\": {\n    \"transformIgnorePatterns\": [\n      \"node_modules/(?!(roughjs|points-on-curve|path-data-parser|points-on-path|browser-nativefs)/)\"\n    ]\n  },\n  \"private\": true,\n  \"scripts\": {\n    \"build\": \"npm run build:app && npm run build:zip\",\n    \"build-node\": \"node ./scripts/build-node.js\",\n    \"build:app\": \"REACT_APP_GIT_SHA=$NOW_GITHUB_COMMIT_SHA react-scripts build\",\n    \"build:zip\": \"node ./scripts/build-version.js\",\n    \"eject\": \"react-scripts eject\",\n    \"fix\": \"npm run fix:other && npm run fix:code\",\n    \"fix:code\": \"npm run test:code -- --fix\",\n    \"fix:other\": \"npm run prettier -- --write\",\n    \"prettier\": \"prettier \\\"**/*.{css,scss,json,md,html,yml}\\\" --ignore-path=.eslintignore\",\n    \"start\": \"react-scripts start\",\n    \"test\": \"npm run test:app\",\n    \"test:all\": \"npm run test:typecheck && npm run test:code && npm run test:other && npm run test:app -- --watchAll=false\",\n    \"test:update\": \"npm run test:app -- --updateSnapshot --watchAll=false\",\n    \"test:app\": \"react-scripts test --env=jsdom --passWithNoTests\",\n    \"test:code\": \"eslint --max-warnings=0 --ignore-path .gitignore --ext .js,.ts,.tsx .\",\n    \"test:debug\": \"react-scripts --inspect-brk test --runInBand --no-cache\",\n    \"test:other\": \"npm run prettier -- --list-different\",\n    \"test:typecheck\": \"tsc\"\n  }\n}\n"
                    }
                  },
                  "cursor": "Y3Vyc29yOjI="
                }],
              "repositoryCount": 2
            }
          }
        }


json_result_python = {
          "data": {
            "search": {
              "edges": [
                {
                  "node": {
                    "nameWithOwner": "CorentinJ/Real-Time-Voice-Cloning",
                    "url": "https://github.com/CorentinJ/Real-Time-Voice-Cloning",
                    "watchers": {
                      "totalCount": 530
                    },
                    "object": {
                      "text": "tensorflow-gpu>=1.10.0,<=1.14.0\numap-learn\nvisdom\nwebrtcvad\nlibrosa>=0.5.1\nmatplotlib>=2.0.2\nnumpy>=1.14.0\nscipy>=1.0.0\ntqdm\nsounddevice\nUnidecode\ninflect\nPyQt5\nmultiprocess\nnumba\n"
                    }
                  },
                  "cursor": "Y3Vyc29yOjE="
                },
                {
                  "node": {
                    "nameWithOwner": "seemoo-lab/opendrop",
                    "url": "https://github.com/seemoo-lab/opendrop",
                    "watchers": {
                      "totalCount": 53
                    },
                    "object": None
                  },
                  "cursor": "Y3Vyc29yOjI="
                }
              ],
              "repositoryCount": 381
            }
          }
        }

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

        # Test month sets to back to 12 (when the diff current-offset is zero)
        offset_date = month_delta(datetime.date(2020, 1, 1), 1)
        self.assertEqual(offset_date.month, 12)
        self.assertEqual(offset_date.year, 2019)  # check year update_popularity_scores

    def test_run_query_github(self):
        """
        Try fetching a month of npm data from the GitHub API
        """

        distant_past = datetime.date(2011, 1, 1)
        github.run_query(distant_past)


    def test_run_query_once_github(self):
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


    def test_write_db_github(self):
        """
        Try writing to the database
        """

        # case for JS
        database = connect_to_db()
        github.write_db(database, json_result_js, 'JavaScript')
        cur = database.cursor()

        cur.execute(
            f"SELECT id FROM applications WHERE name = 'excalidraw/excalidraw';"
        )
        application_id = cur.fetchone()[0]
        self.assertIsInstance(application_id, int)

        cur.execute(
            f"SELECT id FROM packages WHERE name = 'pkg:npm/react@16';"
        )
        package_id = cur.fetchone()[0]
        self.assertIsInstance(package_id, int)

        # case for python
        database = connect_to_db()
        github.write_db(database, json_result_python, 'Python')
        cur = database.cursor()

        cur.execute(
            f"SELECT id FROM applications WHERE name = 'CorentinJ/Real-Time-Voice-Cloning';"
        )
        application_id = cur.fetchone()[0]
        self.assertIsInstance(application_id, int)

        cur.execute(
            f"SELECT id FROM packages WHERE name = 'pkg:pypi/numpy@1';"
        )
        package_id = cur.fetchone()[0]
        self.assertIsInstance(package_id, int)


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

    def test_run_query_pypi(self):
        """
        Try fetching PyPI metadata
        """

        database = connect_to_db()
        cur = database.cursor()
        name = 'pkg:pypi/django@2'
        package_id = insert_to_package(database, name)
        database.commit()
        self.assertIsInstance(package_id, int)
        pypi.run_query()

        cur.execute(
            f"SELECT monthly_downloads_last_month FROM packages WHERE name = '{ name }';"
        )
        monthly_downloads_last_month = cur.fetchone()[0]
        self.assertIsInstance(monthly_downloads_last_month, int)

        cur.execute(
            f"SELECT monthly_downloads_a_year_ago FROM packages WHERE name = '{ name }';"
        )
        monthly_downloads_a_year_ago = cur.fetchone()[0]
        self.assertIsInstance(monthly_downloads_a_year_ago, int)

        cur.execute(
            f"SELECT categories FROM packages WHERE name = '{ name }';"
        )
        categories = cur.fetchone()[0]
        self.assertIsInstance(categories, type(['Utilities', 'Internet']))

        cur.execute(
            f"SELECT modified FROM packages WHERE name = '{ name }';"
        )
        modified = cur.fetchone()[0]
        self.assertIsInstance(modified, datetime.datetime)


        # Test Invalid
        github.MAX_NODES_PER_LOOP=None
        pypi.run_query()
        

    def test_get_package_metadata_npm(self):
        """
        Try to update npm metadata
        """

        # Successful run
        dependency = 'pkg:npm/react@2'
        entry = pypi.get_package_metadata(dependency)
        self.assertIsInstance(entry['monthly_downloads_last_month'], int)
        self.assertIsInstance(entry['monthly_downloads_a_year_ago'], int)
        self.assertIsInstance(entry['categories'], type(['Utilities', 'Internet']))
        self.assertIsInstance(entry['modified'], str)

        # Error run
        dependency = 'pkg:npm/THISPACKAGESHOULDNOTEXIST@2'
        entry = pypi.get_package_metadata(dependency)
        self.assertIsNone(entry['categories'])
        self.assertIsNone(entry['modified'])

    def test_run_query_npm(self):
        """
        Try fetching npm metadata
        """

        database = connect_to_db()
        cur = database.cursor()
        name = 'pkg:npm/react@3'
        package_id = insert_to_package(database, name)
        database.commit()
        self.assertIsInstance(package_id, int)
        npm.run_query()

        cur.execute(
            f"SELECT monthly_downloads_last_month FROM packages WHERE name = '{ name }';"
        )
        monthly_downloads_last_month = cur.fetchone()[0]
        self.assertIsInstance(monthly_downloads_last_month, int)

        cur.execute(
            f"SELECT monthly_downloads_a_year_ago FROM packages WHERE name = '{ name }';"
        )
        monthly_downloads_a_year_ago = cur.fetchone()[0]
        self.assertIsInstance(monthly_downloads_a_year_ago, int)

        cur.execute(
            f"SELECT categories FROM packages WHERE name = '{ name }';"
        )
        categories = cur.fetchone()[0]
        self.assertIsInstance(categories, type(['Utilities', 'Internet']))

        cur.execute(
            f"SELECT modified FROM packages WHERE name = '{ name }';"
        )
        modified = cur.fetchone()[0]
        self.assertIsInstance(modified, datetime.datetime)

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
