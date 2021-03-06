"""
Test the recommender service
"""

from unittest import TestCase
import json
from webservice.github_util import javascript_dependencies_name_to_purl
from webservice.recommender_service import RecommenderService
from .samples.sample_package_json import SAMPLE_PACKAGE_JSON


class TestRecommenderService(TestCase):
    """
    Tests for the recommender service
    """

    def setUp(self):
        recommender_service = RecommenderService()

        purl_dependencies = javascript_dependencies_name_to_purl(
            json.loads(SAMPLE_PACKAGE_JSON)['dependencies'])

        self.recommendations = recommender_service.get_recommendations(purl_dependencies)

    def test_get_recommendations_count(self):
        """
        Make sure we can fetch recommendations
        """

        self.assertGreater(len(self.recommendations), 11)

    def test_get_recommendation_content(self):
        """
        Make sure each recommendation is formatted as we expect
        """

        for recommendation in self.recommendations:
            self.assertEqual(11, len(recommendation))

            # Make sure every entry (except for categories and date) exists
            self.assertIsNotNone(recommendation[0])
            self.assertIsNotNone(recommendation[1])
            self.assertIsNotNone(recommendation[2])
            self.assertIsNotNone(recommendation[3])
            self.assertIsNotNone(recommendation[4])
            self.assertIsNotNone(recommendation[5])
            self.assertIsNotNone(recommendation[6])
            self.assertIsNotNone(recommendation[7])
