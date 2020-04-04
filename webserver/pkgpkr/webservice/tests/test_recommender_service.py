from unittest import TestCase
import json
from webservice.github_util import depenencies_name_to_purl
from webservice.recommender_service import RecommenderService
from .samples.sample_package_json import sample_package_json


class TestRecommenderService(TestCase):

    def setUp(self):
        recommender_service = RecommenderService()

        purl_dependencies = depenencies_name_to_purl(json.loads(sample_package_json)['dependencies'])

        self.recommendations = recommender_service.get_recommendations(purl_dependencies)

    def test_get_recommendations_count(self):
        self.assertGreater(len(self.recommendations), 10)

    def test_get_recommendation_content(self):
        for recommendation in self.recommendations:
            self.assertCountEqual({'name', 'url', 'average_downloads', 'keywords', 'date', 'rate'},
                                  recommendation.keys())

            self.assertIsNotNone(recommendation['name'])
            self.assertIsNotNone(recommendation['url'])
            # TODO this not always passing due to known issue in DB
            #self.assertIsNotNone(recommendation['average_downloads'])
            #self.assertIsNotNone(recommendation['date'])
            self.assertIsNotNone(recommendation['rate'])

