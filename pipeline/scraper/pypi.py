"""
Fetch package metadata from the pypi API
"""

import json
import requests
import pypistats
from scraper.psql import connect_to_db, update_package_metadata


PYPI_DEPENDENCY_META_URL = 'https://pypi.python.org/pypi/'


def run_query():
    """
    Enrich the package table with metadata for all packages in the table
    """

    # Connect to the database
    database = connect_to_db()
    cur = database.cursor()

    # Fetch all package names from the database
    cur.execute("SELECT name FROM packages WHERE name LIKE 'pkg:pypi/%';")
    results = [result[0] for result in cur.fetchall()]

    # Fetch all metadata for the packages from npmjs.com and write to the database
    for result in results:
        print(f"Fetching metadata for {result}")
        metadata = get_package_metadata(result)
        update_package_metadata(database,
                                metadata.get('name'),
                                metadata.get('monthly_downloads_last_month'),
                                metadata.get('monthly_downloads_a_year_ago'),
                                metadata.get('categories'),
                                metadata.get('modified'))

        # Commit the changes to the database
        database.commit()

    # Clean up the database connection
    cur.close()
    database.close()


def get_package_metadata(dependency):
    """
    Retrieve the downloads, categories, and modified date for a package from pypi API
    """

    version_symbol_index = dependency.rfind('@')
    name_index = dependency.find('/') + 1
    dependency_name = dependency[name_index:version_symbol_index]

    entry = dict()

    entry['name'] = dependency

    request_url = f'{PYPI_DEPENDENCY_META_URL}{dependency_name}/json'
    try:
        result = json.loads(pypistats.recent(dependency_name, "month", format="json"))
        entry['monthly_downloads_last_month'] = result['data']['last_month']
        entry['monthly_downloads_a_year_ago'] = 0
        json_result = requests.get(request_url).json()

    # pylint: disable=bare-except
    except:
        print(f"Could not request {request_url}")
        entry['categories'] = None
        entry['modified'] = None
        return entry

    try:
        entry['categories'] = []
        for item in json_result['info']['classifiers']:
            if "Topic :: " in item:
                entry['categories'].insert(-1, item.replace("Topic :: ", ""))
    except KeyError as exc:
        print(f"Could not fetch categories for {dependency_name}: {exc}")
        entry['categories'] = []

    try:
        entry['modified'] = json_result['urls'][0]['upload_time_iso_8601']
    except (KeyError, IndexError) as exc:
        print(f"Could not fetch modified date for {dependency_name}: {exc}")
        entry['modified'] = None
    print(f"pypi entry: {entry}")
    return entry
