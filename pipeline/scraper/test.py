"""
Test script for the ML pipeline scraper

To run the test, use the following command under the pipeline/ folder:

```
DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD DB_HOST=$DB_HOST TOKEN=$TOKEN \
    python3 -m unittest scraper/test.py -v
```
"""

import unittest
import datetime
from PSQL import connectToDB
from PSQL import insertToApplication
from PSQL import insertToDependencies
from PSQL import insertToPackages
from PSQL import updatePackageMetadata
from GitHubQuery import runQueryOnce

def make_orderer():
    """
    Create helper functions for sorting and comparing objects
    """

    order = {}

    def orderer(obj):
        order[obj.__name__] = len(order)
        return obj

    def comparator(obj_a, obj_b):
        return [1, -1][order[obj_a] < order[obj_b]]

    return orderer, comparator

ORDERED, COMPARE = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = COMPARE

class TestMyClass(unittest.TestCase):
    """
    Tests for the ML pipeline scraper
    """

    @ORDERED
    def test_run_query_once(self):
        """
        Try fetching data from the GitHub API
        """

        month_str = "created:2020-01-01..2020-02-01"
        cursor = None
        for i in [1, 10, 100]:
            try:
                result = runQueryOnce(i, month_str, cursor)
                self.assertIsNotNone(result['data']['search']['edges'])
            except ValueError:
                self.assertIsNone(result['data']['search']['edges'])


    @ORDERED
    def test_connect_to_db(self):
        """
        Try connecting to the database
        """

        database = connectToDB()
        self.assertIsNotNone(database)


    @ORDERED
    def test_insert_to_application(self):
        """
        Try inserting an application into the application table
        """

        database = connectToDB()
        url = "www.pkgpkr.com"
        followers = 314
        app_name = "pkgpkr"
        my_hash = hash(app_name)
        app_id = insertToApplication(database, url, followers, app_name, my_hash)
        self.assertIsInstance(app_id, int)
        cur = database.cursor()
        cur.execute(
            "SELECT name FROM applications WHERE id = %s;" % (app_id)
        )
        application_name = cur.fetchone()[0]
        self.assertEqual(application_name, app_name)


    @ORDERED
    def test_insert_to_packages(self):
        """
        Try inserting a package into the package table
        """

        database = connectToDB()
        name = "myPkg"
        package_id = insertToPackages(database, name)
        self.assertIsInstance(package_id, int)
        cur = database.cursor()
        cur.execute(
            "SELECT name FROM packages WHERE id = %s;" % (package_id)
        )
        package_name = cur.fetchone()[0]
        self.assertEqual(package_name, name)


    @ORDERED
    def test_update_package_metadata(self):
        """
        Try to update the metadata associated with a package
        """

        database = connectToDB()
        name = "myPkg"
        downloads_last_month = 200
        categories = ["critical", ",,comma", "\\{braces\\}", "\'quoted\""]
        modified = datetime.datetime.now()

        # Insert package into the table
        package_id = insertToPackages(database, name)
        self.assertIsInstance(package_id, int)

        # Ensure that the modified field is None
        cur = database.cursor()
        cur.execute(
            "SELECT modified FROM packages WHERE id = %s;" % (package_id)
        )
        modified_date = cur.fetchone()[0]
        self.assertIsNone(modified_date)

        # Update metadata in the table
        updatePackageMetadata(database, name, downloads_last_month, categories, modified)

        # Ensure that the modified field is now not None
        cur.execute(
            "SELECT modified FROM packages WHERE id = %s;" % (package_id)
        )
        modified_date = cur.fetchone()[0]
        self.assertIsNotNone(modified_date)

        # Upsert the same package into the table again
        package_id = insertToPackages(database, name)
        self.assertIsInstance(package_id, int)

        # Ensure that the modified field is still not None
        cur.execute(
            "SELECT modified FROM packages WHERE id = %s;" % (package_id)
        )
        modified_date = cur.fetchone()[0]
        self.assertIsNotNone(modified_date)


    @ORDERED
    def test_insert_to_dependencies(self):
        """
        Try to insert a dependency into the dependency table
        """

        database = connectToDB()
        url = "www.pkgpkr.com"
        followers = 314
        app_name = "pkgpkr"
        my_hash = hash(app_name)
        application_id = insertToApplication(database, url, followers, app_name, my_hash)
        name = "myPkg"
        package_id = insertToPackages(database, name)
        insertToDependencies(database, application_id, package_id)
        cur = database.cursor()
        cur.execute(
            "SELECT * FROM dependencies WHERE application_id = %s AND package_id = %s;"
            % (application_id, package_id)
        )
        result = cur.fetchall()
        self.assertEqual(result, [(application_id, package_id)])

if __name__ == "__main__":
    unittest.main()
