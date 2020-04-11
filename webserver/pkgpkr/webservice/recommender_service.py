"""
Get package recommendations from our database
"""

import math
import re
import psycopg2

from pkgpkr.settings import DB_HOST
from pkgpkr.settings import DB_USER
from pkgpkr.settings import DB_PASSWORD
from pkgpkr.settings import NPM_DEPENDENCY_BASE_URL

class RecommenderService:

    def __init__(self):

        self.majorVersionRegex = re.compile(r'pkg:npm/.*@\d+')
        self.nameOnlyRegex = re.compile(r'pkg:npm/(.*)@\d+')

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
        # 2. Get a list of all similarity scores involving those packages
        # 3. Get the names and similarity scores of those packages
        cur.execute(f"""
                    SELECT a.name, b.name, s.similarity, b.downloads_last_month, b.categories, b.modified
                    FROM similarity s
                    INNER JOIN packages a ON s.package_a = a.id
                    INNER JOIN packages b ON s.package_b = b.id
                    WHERE s.package_a IN (
                        SELECT DISTINCT id FROM packages WHERE name in ({str(packages)[1:-1]})
                    )
                    """)

        # Add recommendations (including metadata) to results
        recommended = []
        for result in cur.fetchall():

            # Format metadata
            package = result[0].replace("pkg:npm/", "", 1)
            recommendation = result[1].replace("pkg:npm/", "", 1)
            url = f"{NPM_DEPENDENCY_BASE_URL}/{self.nameOnlyRegex.search(result[1]).group(1)}"
            similarity = math.ceil(10 * result[2])
            day = result[5]
            if day:
                day = day.strftime('%Y-%m-%d')

            # Add to the list of recommendations
            recommended.append(
                {
                    'package': package,
                    'recommendation': recommendation,
                    'url': url,
                    'similarity': similarity,
                    'average_downloads': result[3],
                    'keywords': result[4],
                    'date': day
                }
            )

        # Disconnect from the database
        cur.close()
        db.close()

        return recommended
