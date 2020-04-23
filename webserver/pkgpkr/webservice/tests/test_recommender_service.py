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
            self.assertCountEqual(
                {
                    'package',
                    'recommendation',
                    'url',
                    'absolute_trend_score',
                    'relative_trend_score',
                    'popularity_score',
                    'similarity_score',
                    'overall_score',
                    'keywords',
                    'date'
                },
                recommendation.keys()
            )

            self.assertIsNotNone(recommendation['package'])
            self.assertIsNotNone(recommendation['recommendation'])
            self.assertIsNotNone(recommendation['url'])
            self.assertIsNotNone(recommendation['absolute_trend_score'])
            self.assertIsNotNone(recommendation['relative_trend_score'])
            self.assertIsNotNone(recommendation['popularity_score'])
            self.assertIsNotNone(recommendation['similarity_score'])
            self.assertIsNotNone(recommendation['overall_score'])
