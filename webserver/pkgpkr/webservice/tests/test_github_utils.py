"""
Test the utility functions for GitHub
"""

import os

from unittest import TestCase

from webservice.github_util import dependencies_name_to_purl
from webservice.github_util import parse_dependencies
from webservice.github_util import get_user_info
from webservice.github_util import is_user_authenticated
from webservice.github_util import get_user_name
from webservice.github_util import get_repositories
from webservice.github_util import get_dependencies

from .samples.sample_package_json import SAMPLE_PACKAGE_JSON

class TestGithubUtil(TestCase):
    """
    Tests for the GitHub utility functions
    """

    def setUp(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')

    def test_get_user_info(self):
        """
        Ensure we can get the user info associated with a GitHub token
        """

        user_info = get_user_info(self.github_token)

        self.assertIn('id', user_info.keys())
        self.assertIn('name', user_info.keys())
        self.assertIn('location', user_info.keys())

    def test_is_user_authenticated(self):
        """
        Ensure we can check whether a user is authenticated
        """

        self.assertTrue(is_user_authenticated(self.github_token))
        self.assertFalse(is_user_authenticated('BAD TOKEN'))

    def test_get_user_name(self):
        """
        Ensure that the user name associated with our token is what we expect
        """

        self.assertEqual(get_user_name(self.github_token), 'pkgpkr1')

    def test_get_repositories(self):
        """
        Ensure that we can get repositories associated with our token
        """

        repos = get_repositories(self.github_token)

        self.assertLessEqual(len(repos), 100)
        self.assertIn('pkgpkr1/express', [repo['nameWithOwner'] for repo in repos])

    def test_dependencies_name_to_purl(self):
        """
        Ensure that we can convert dependency names to PURL format
        """

        depencencies = {
            "accepts": "~1.3.7",
            "array-flatten": "^1.1.1",
            "content-type": "~1.0.4",
            "cookie": "0.4.0",
            "qs": "6.7.0"
        }

        purl_dependencies = dependencies_name_to_purl(depencencies)

        # Assure each of expected values are in the returned list
        self.assertIn('pkg:npm/accepts@1.3.7', purl_dependencies)
        self.assertIn('pkg:npm/array-flatten@1.1.1', purl_dependencies)
        self.assertIn('pkg:npm/content-type@1.0.4', purl_dependencies)
        self.assertIn('pkg:npm/cookie@0.4.0', purl_dependencies)
        self.assertIn('pkg:npm/qs@6.7.0', purl_dependencies)

        # Assure length is same
        self.assertEqual(len(purl_dependencies), len(depencencies.keys()))

    def test_get_dependencies(self):
        """
        Ensure that a repository has a package we expect
        """

        dependencies, branch_names = get_dependencies(self.github_token, 'pkgpkr1/express', 'master')

        # For partial match, e.g pkg:npm/accepts@1.3.7 -> pkg:npm/accepts
        must_include_package = 'pkg:npm/accepts'

        includes_package = False

        for dependency in dependencies:
            if must_include_package in dependency:
                includes_package = True

        self.assertTrue(includes_package)


        # Assure branch names contains specific branches

        self.assertIn('master', branch_names)
        self.assertIn('test', branch_names)
        self.assertNotIn('branch-that-does-not-exist', branch_names)

    def test_parse_dependencies(self):
        """
        Ensure that we can parse a sample package.json object
        """

        # Get dependencies
        dependencies = parse_dependencies(SAMPLE_PACKAGE_JSON)

        # Assure at least 5 predictions
        self.assertGreaterEqual(len(dependencies), 5)

        count = 0

        # Count how often npm dependency is found
        for dependency in dependencies:
            if 'pkg:npm/' in dependency:
                count += 1

        # Assure at least five start with 'pkg:npm/'
        self.assertGreaterEqual(count, 5)
