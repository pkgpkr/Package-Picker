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
        self.max_recommendations = 1000

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
        # 2. Fetch recommendations but deduplicate them by keeping the highest score
        # 3. Return a list of recommendations with the package for which they were recommended
        # 4. Exclude any recommendations for packages that appear in the dependencies already
        # 5. Limit results to 1,000 for performance (we should figure out how to raise this)
        #
        packages = self.strip_to_major_version(dependencies)
        cur.execute(f"""
                    SELECT DISTINCT ON (b.name) a.name, b.name, s.similarity, b.downloads_last_month, b.categories, b.modified
                    FROM similarity s
                    INNER JOIN packages a ON s.package_a = a.id
                    INNER JOIN packages b ON s.package_b = b.id
                    WHERE
                    s.package_a IN (SELECT id FROM packages WHERE name in ({str(packages)[1:-1]}))
                    AND
                    s.package_b NOT IN (SELECT id FROM packages WHERE name in ({str(packages)[1:-1]}))
                    ORDER BY b.name, s.similarity DESC
                    LIMIT {self.max_recommendations}
                    """)

        # Add recommendations (including metadata) to results
        recommended = []
        for result in cur.fetchall():

            # Format metadata
            package = result[0].replace("pkg:npm/", "", 1)
            recommendation = result[1].replace("pkg:npm/", "", 1)
            url = f"{NPM_DEPENDENCY_BASE_URL}/{self.name_only_regex.search(result[1]).group(1)}"
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
        database.close()

        return recommended
