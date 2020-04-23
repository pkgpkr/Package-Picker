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
    """
    Recommender engine for the web server
    """

    def __init__(self):

        self.major_version_regex = re.compile(r'pkg:npm/.*@\d+')
        self.name_only_regex = re.compile(r'pkg:npm/(.*)@\d+')
        self.max_recommendations = 10000

    def strip_to_major_version(self, dependencies):
        """
        Strip everything after the major version in each dependency
        """

        packages = []
        for dependency in dependencies:
            match = self.major_version_regex.search(dependency)
            if not match:
                continue
            packages.append(match.group())

        return packages

    def get_recommendations(self, dependencies):
        """
        Return a list of package recommendations and metadata given a set of dependencies
        """

        # Connect to our database
        database = psycopg2.connect(f"host={DB_HOST} user={DB_USER} password={DB_PASSWORD}")
        cur = database.cursor()

        # Get recommendations from our model
        #
        # 1. Get a list of identifiers for the packages passed into this method
        # 2. Fetch recommendations with the following scores:
        #    1. Similarity score
        #    2. Popularity score
        #    3. Absolute trend score
        #    4. Percent trend score
        # 3. Return a list of recommendations with the package for which they were recommended
        # 4. Exclude any recommendations for packages that appear in the dependencies already
        # 5. Limit results to 1,000 for performance (we should figure out how to raise this)
        #
        packages = self.strip_to_major_version(dependencies)
        cur.execute(f"""
                    SELECT
                    REPLACE(a.name, 'pkg:npm/', ''),
                    REPLACE(b.name, 'pkg:npm/', ''),
                    CONCAT('{NPM_DEPENDENCY_BASE_URL}/', REGEXP_REPLACE(b.name, 'pkg:npm/(.*)@\\d+', '\\1')),
                    CEIL(CEIL(10 * s.similarity) * 0.5 + b.bounded_popularity * 0.3 + b.absolute_trend * 0.1 + b.relative_trend * 0.1),
                    b.absolute_trend,
                    b.relative_trend,
                    b.bounded_popularity,
                    CEIL(10 * s.similarity),
                    b.categories,
                    TO_CHAR(b.modified, 'yyyy-mm-dd')
                    FROM similarity s
                    INNER JOIN packages a ON s.package_a = a.id
                    INNER JOIN packages b ON s.package_b = b.id
                    WHERE
                    s.package_a IN (SELECT id FROM packages WHERE name in ({str(packages)[1:-1]}))
                    AND
                    s.package_b NOT IN (SELECT id FROM packages WHERE name in ({str(packages)[1:-1]}))
                    ORDER BY s.similarity DESC
                    LIMIT {self.max_recommendations}
                    """)

        # Fetch results
        recommended = cur.fetchall()

        # Disconnect from the database
        cur.close()
        database.close()

        return recommended
