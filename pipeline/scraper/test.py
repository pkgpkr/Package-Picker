# Test Script
# To run test, DB_USER=postgres DB_PASSWORD=secret DB_HOST=localhost TOKEN=<token> python3 -m unittest test.py -v in the scraper folder

import PSQL
import GraphQLQuery
import unittest
import json
import urllib

def make_orderer():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare

ordered, compare = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = compare

class TestMyClass(unittest.TestCase):

    @ordered
    def test_runQuery(self):
        return
    

    @ordered
    def test_runQueryOnce(self):
        monthStr = "created:2020-01-01..2020-02-01"
        for i in [1,10,100]: 
            result = GraphQLQuery.runQueryOnce(i, monthStr)
            json_obj = None
            try:
                json_obj = json.load(result)
                print(json_obj)
                self.assertTrue(json_obj is not None)
            except:
                self.assertFalse(json_obj is not None)
    

    @ordered
    def test_connectToDB(self):
        db = PSQL.connectToDB()
        self.assertTrue(db is not None)


    @ordered
    def test_insertToApplication(self):
        db = PSQL.connectToDB()
        url = "www.pkgpkr.com"
        followers = 314
        appName = "pkgpkr"
        myHash = hash(appName)
        id = PSQL.insertToApplication(db,url,followers,appName,myHash)
        self.assertTrue(type(id) == int)
        cur = db.cursor()
        cur.execute(
            "SELECT name FROM applications WHERE id = %s;" % (id)
        )
        application_name = cur.fetchone()[0]
        self.assertTrue(application_name == appName)


    @ordered
    def test_insertToPackages(self):
        db = PSQL.connectToDB()
        name = "myPkg"
        id = PSQL.insertToPackages(db,name)
        self.assertTrue(type(id) == int)
        cur = db.cursor()
        cur.execute(
            "SELECT name FROM packages WHERE id = %s;" % (id)
        )
        package_name = cur.fetchone()[0]
        self.assertTrue(package_name == name)


    @ordered
    def test_insertToDependencies(self):
        db = PSQL.connectToDB()
        url = "www.pkgpkr.com"
        followers = 314
        appName = "pkgpkr"
        myHash = hash(appName)
        application_id = PSQL.insertToApplication(db,url,followers,appName,myHash)
        name = "myPkg"
        package_id = PSQL.insertToPackages(db,name)
        PSQL.insertToDependencies(db, application_id, package_id)
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM dependencies WHERE application_id = %s AND package_id = %s;"
            % (application_id, package_id)
        )
        result = cur.fetchall()
        self.assertTrue(result == [(application_id, package_id)])

if __name__ == "__main__":
    unittest.main()