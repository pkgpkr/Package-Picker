"""
Test the utility functions for GitHub
"""

import os

from unittest import TestCase

from pkgpkr.settings import SUPPORTED_LANGUAGES, JAVASCRIPT, PYTHON
from webservice.github_util import javascript_dependencies_name_to_purl, python_dependencies_name_to_purl
from webservice.github_util import parse_dependencies
from webservice.github_util import get_user_info
from webservice.github_util import is_user_authenticated
from webservice.github_util import get_user_name
from webservice.github_util import get_repositories
from webservice.github_util import get_dependencies
from webservice.tests.samples.sample_requirements_txt import SAMPLE_REQUIREMNTS_TXT

from .samples.sample_package_json import SAMPLE_PACKAGE_JSON


class TestGithubUtil(TestCase):
    """
    Tests for the GitHub utility functions
    """

    def setUp(self):
        self.github_token = os.environ.get('GH_TOKEN')

        self.language_to_sampe_file_map = {JAVASCRIPT: SAMPLE_PACKAGE_JSON,
                                           PYTHON: SAMPLE_REQUIREMNTS_TXT}

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

        javascript_repos = repos[JAVASCRIPT]
        self.assertIn('pkgpkr1/express', [repo['nameWithOwner'] for repo in javascript_repos])

        python_repos = repos[PYTHON]
        self.assertIn('pkgpkr1/inter', [repo['nameWithOwner'] for repo in python_repos])

    def test_javascript_dependencies_name_to_purl(self):
        """
        Ensure that we can convert Javascript dependency names to PURL format
        """

        depencencies = {
            "accepts": "~1.3.7",
            "array-flatten": "^1.1.1",
            "content-type": "~1.0.4",
            "cookie": "0.4.0",
            "qs": "6.7.0"
        }

        purl_dependencies = javascript_dependencies_name_to_purl(depencencies)

        # Assure each of expected values are in the returned list
        self.assertIn('pkg:npm/accepts@1.3.7', purl_dependencies)
        self.assertIn('pkg:npm/array-flatten@1.1.1', purl_dependencies)
        self.assertIn('pkg:npm/content-type@1.0.4', purl_dependencies)
        self.assertIn('pkg:npm/cookie@0.4.0', purl_dependencies)
        self.assertIn('pkg:npm/qs@6.7.0', purl_dependencies)

        # Assure length is same
        self.assertEqual(len(purl_dependencies), len(depencencies.keys()))

    def test_python_dependencies_name_to_purl(self):
        """
        Ensure that we can convert Python dependency names to PURL format
        """

        depencencies = """
            fonttools[lxml,unicode,ufo]>=4.0.2
            ufo2ft[pathops]<=2.9.1
            defcon[lxml]===0.6.0
            skia-pathops
            # only used for DesignSpaceDocumentReader in fontbuild
            MutatorMath==2.1.2rc0
            # for woff2
            brotli>=1.0.7, <1.0.3
            joblib>1.0.7, <=1.0.3
            requests>0.0.1
            $$$NOT A DEPENDENCY, SHOULD NOT BE PARSED$$$
        """

        purl_dependencies = python_dependencies_name_to_purl(depencencies)

        # Assure each of expected values are in the returned list
        self.assertIn('pkg:pypi/fonttools@4.0.2', purl_dependencies)
        self.assertIn('pkg:pypi/ufo2ft@2.9.1', purl_dependencies)
        self.assertIn('pkg:pypi/defcon@0.6.0', purl_dependencies)
        self.assertIn('pkg:pypi/skia-pathops', purl_dependencies)
        self.assertIn('pkg:pypi/MutatorMath@2.1.2rc0', purl_dependencies)
        self.assertIn('pkg:pypi/brotli@1.0.7', purl_dependencies)
        self.assertIn('pkg:pypi/joblib@1.0.3', purl_dependencies)
        self.assertIn('pkg:pypi/requests', purl_dependencies)

        # Assure length is same
        self.assertEqual(len(purl_dependencies), 8)

    def test_get_dependencies(self):
        """
        Ensure that a repository has a package we expect
        """

        dependencies, branch_names, language = get_dependencies(self.github_token, 'pkgpkr1/express', 'master')

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
        self.assertEqual('javascript', language)

    def test_parse_dependencies(self):
        """
        Ensure that we can parse a sample package.json object
        """
        for language, language_attributes in SUPPORTED_LANGUAGES.items():
            # Get dependencies
            dependencies = parse_dependencies(dependencies_string=self.language_to_sampe_file_map[language],
                                              language=language,
                                              is_from_github=True)

            # Assure at least 5 predictions
            self.assertGreaterEqual(len(dependencies), 5)
