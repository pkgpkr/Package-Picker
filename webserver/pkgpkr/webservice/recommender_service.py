"""
Get package recommendations from our database
"""

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
        # 2. Get the identifier for every package that is similar to those packages
        # 3. Get the names and similarity scores of those packages
        packages = self.strip_to_major_version(dependencies)
        cur.execute(f"""
                    SELECT packages.name, packages.downloads_last_month, packages.categories, packages.modified, s.similarity FROM packages INNER JOIN (
                        SELECT package_b, MAX(similarity) AS similarity FROM similarity WHERE package_a IN (
                            SELECT DISTINCT id FROM packages WHERE name in ({str(packages)[1:-1]})
                        ) GROUP BY package_b
                    ) s ON s.package_b = packages.id
                    """)

        # Add recommendations (including metadata) to results
        recommended = []
        for result in cur.fetchall():
            url = f"{NPM_DEPENDENCY_BASE_URL}/{self.name_only_regex.search(result[0]).group(1)}"
            recommended.append(
                {
                    'name': result[0],
                    'url': url,
                    'average_downloads': result[1],
                    'keywords': result[2],
                    'date': result[3],
                    'rate': result[4]
                }
            )

        # Disconnect from the database
        cur.close()
        database.close()

        return recommended
