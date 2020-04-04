from unittest import TestCase

from webservice.github_util import depenencies_name_to_purl, parse_dependencies, get_user_info, is_user_authenticated, \
    get_user_name, get_repositories, get_dependencies

from .samples.sample_package_json import sample_package_json

import os
import json


class TestGithubUtil(TestCase):

    def setUp(self):
        self.github_token = os.environ.get('TOKEN')

    def test_get_user_info(self):
        user_info = get_user_info(self.github_token)

        self.assertIn('id', user_info.keys())
        self.assertIn('name', user_info.keys())
        self.assertIn('location', user_info.keys())

    def test_is_user_authenticated(self):
        self.assertTrue(is_user_authenticated(self.github_token))
        self.assertFalse(is_user_authenticated('BAD TOKEN'))

    def test_get_user_name(self):
        self.assertEqual(get_user_name(self.github_token), 'pkgpkr1')

    def test_get_repositories(self):
        repos = get_repositories(self.github_token)

        self.assertLessEqual(len(repos), 100)
        self.assertIn('pkgpkr1/express', [repo['nameWithOwner'] for repo in repos])

    def test_depenencies_name_to_purl(self):
        depencencies = {
            "accepts": "~1.3.7",
            "array-flatten": "^1.1.1",
            "content-type": "~1.0.4",
            "cookie": "0.4.0",
            "qs": "6.7.0"
        }

        purl_dependencies = depenencies_name_to_purl(depencencies)

        # Assure each of expected values are in the returned list
        self.assertIn('pkg:npm/accepts@1.3.7', purl_dependencies)
        self.assertIn('pkg:npm/array-flatten@1.1.1', purl_dependencies)
        self.assertIn('pkg:npm/content-type@1.0.4', purl_dependencies)
        self.assertIn('pkg:npm/cookie@0.4.0', purl_dependencies)
        self.assertIn('pkg:npm/qs@6.7.0', purl_dependencies)

        # Assure length is same
        self.assertEqual(len(purl_dependencies), len(depencencies.keys()))

    def test_get_dependencies(self):
        """token, repo_full_name"""
        dependencies = get_dependencies(self.github_token, 'pkgpkr1/express')

        # For partial match, e.g pkg:npm/accepts@1.3.7 -> pkg:npm/accepts
        must_include_package = 'pkg:npm/accepts'

        includes_package = False

        for dependency in dependencies:
            if must_include_package in dependency:
                includes_package = True

        self.assertTrue(includes_package)

    def test_parse_dependencies(self):
        # set localhost if not passed to DOMAIN NAME

        dependencies = parse_dependencies(sample_package_json)

        # Assure at least 5 predictions
        self.assertGreaterEqual(len(dependencies), 5)

        count = 0

        for dependency in dependencies:
            if 'pkg:npm/' in dependency:
                count += 1

        # Assure at least five start with 'pkg:nmp/'
        self.assertGreaterEqual(count, 5)
