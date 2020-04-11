"""
Test the recommender service
"""

from unittest import TestCase
import json
from webservice.github_util import dependencies_name_to_purl
from webservice.recommender_service import RecommenderService
from .samples.sample_package_json import SAMPLE_PACKAGE_JSON


class TestRecommenderService(TestCase):
    """
    Tests for the recommender service
    """

    def setUp(self):
        recommender_service = RecommenderService()

        purl_dependencies = dependencies_name_to_purl(
            json.loads(SAMPLE_PACKAGE_JSON)['dependencies'])

        self.recommendations = recommender_service.get_recommendations(purl_dependencies)

    def test_get_recommendations_count(self):
        """
        Make sure we can fetch recommendations
        """

        self.assertGreater(len(self.recommendations), 10)

    def test_get_recommendation_content(self):
        """
        Make sure each recommendation is formatted as we expect
        """

        for recommendation in self.recommendations:
            self.assertCountEqual({'name', 'url', 'average_downloads', 'keywords', 'date', 'rate'},
                                  recommendation.keys())

            self.assertIsNotNone(recommendation['name'])
            self.assertIsNotNone(recommendation['url'])
            self.assertIsNotNone(recommendation['average_downloads'])
            self.assertIsNotNone(recommendation['rate'])
