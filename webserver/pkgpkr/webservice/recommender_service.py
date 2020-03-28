import requests
import random
import psycopg2
import os
import re

from pkgpkr.settings import DB_HOST
from pkgpkr.settings import DB_USER
from pkgpkr.settings import DB_PASSWORD

class RecommenderService:

    def __init__(self):

        self.majorVersionRegex = re.compile(r'pkg:npm/.*@\d+')

    def get_recommendations(self, dependencies):

        # Strip everything after the major version
        packages = []
        for dependency in dependencies:
            match = self.majorVersionRegex.search(dependency)
            if not match:
                continue
            packages.append(match.group())

        # Connect to our database
        db = psycopg2.connect(f"host={DB_HOST} user={DB_USER} password={DB_PASSWORD}")
        cur = db.cursor()

        # Get recommendations from our model
        #
        # 1. Get a list of identifiers for the packages passed into this method
        # 2. Get the identifier for every package that is similar to those packages
        # 3. Get the names and similarity scores of those packages
        cur.execute(f"""
                    SELECT packages.name, packages.downloads_last_month, packages.categories, packages.modified, s.similarity FROM packages INNER JOIN (
                        SELECT package_b, MAX(similarity) AS similarity FROM similarity WHERE package_a IN (
                            SELECT DISTINCT id FROM packages WHERE name in ({str(packages)[1:-1]})
                        ) GROUP BY package_b
                    ) s ON s.package_b = packages.id
                    """)
        recommended = [{'name': result[0], 'average_downloads': result[1], 'keywords': result[2], 'date': result[3], 'rate': result[4]} for result in cur.fetchall()]

        # Disconnect from the database
        cur.close()
        db.close()

        return recommended
