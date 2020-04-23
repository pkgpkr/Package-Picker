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
                    SELECT a.name, b.name, b.absolute_trend, b.relative_trend, b.bounded_popularity, s.similarity, b.categories, b.modified
                    FROM similarity s
                    INNER JOIN packages a ON s.package_a = a.id
                    INNER JOIN packages b ON s.package_b = b.id
                    WHERE
                    s.package_a IN (SELECT id FROM packages WHERE name in ({str(packages)[1:-1]}))
                    AND
                    s.package_b NOT IN (SELECT id FROM packages WHERE name in ({str(packages)[1:-1]}))
                    LIMIT {self.max_recommendations}
                    """)

        # Add recommendations (including metadata) to results
        recommended = []
        for result in cur.fetchall():

            # Package name
            package = result[0].replace("pkg:npm/", "", 1)

            # Recommendation name
            recommendation = result[1].replace("pkg:npm/", "", 1)

            # Recommendation URL
            url = f"{NPM_DEPENDENCY_BASE_URL}/{self.name_only_regex.search(result[1]).group(1)}"

            # Similarity score
            similarity_score = math.ceil(10 * result[5])

            # Popularity score
            popularity_score = result[4]

            # Absolute trend score
            absolute_trend_score = result[2]

            # Relative trend score
            relative_trend_score = result[3]

            # Weighted overall score
            weighted_similarity = 0
            weighted_popularity = 0
            weighted_absolute_trend = 0
            weighted_relative_trend = 0
            if similarity_score:
                weighted_similarity = similarity_score * 0.5
            if popularity_score:
                weighted_popularity = popularity_score * 0.3
            if absolute_trend_score:
                weighted_absolute_trend = absolute_trend_score * 0.1
            if relative_trend_score:
                weighted_relative_trend = relative_trend_score * 0.1
            overall_score = math.ceil(weighted_similarity + weighted_popularity + weighted_absolute_trend + weighted_relative_trend)

            # Keywords
            keywords = result[6]

            # Modified date
            day = result[7]
            if day:
                day = day.strftime('%Y-%m-%d')

            # Add to the list of recommendations
            recommended.append(
                [
                    package,
                    [
                        recommendation,
                        url
                    ],
                    overall_score,
                    absolute_trend_score,
                    relative_trend_score,
                    popularity_score,
                    similarity_score,
                    keywords,
                    day
                ]
            )

        # Disconnect from the database
        cur.close()
        database.close()

        return recommended
