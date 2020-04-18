"""
Fetch package metadata from the pypi API
"""

import requests
from psql import connect_to_db, update_package_metadata
import pypistats
import json
import xmlrpc.client

PYPI_DEPENDENCY_META_URL = 'http://pypi.python.org/pypi/'


def run_query():
    """
    Enrich the package table with metadata for all packages in the table
    """

    # Connect to the database
    database = connect_to_db()
    cur = database.cursor()

    # Fetch all package names from the database
    cur.execute("SELECT name FROM packages;")
    results = [result[0] for result in cur.fetchall()]

    # Fetch all metadata for the packages from npmjs.com and write to the database
    for result in results:
        print(f"Fetching metadata for {result}")
        metadata = get_package_metadata(result)
        update_package_metadata(database,
                                metadata['name'],
                                metadata['downloads_last_month'],
                                metadata['categories'],
                                metadata['modified'])

        # Commit the changes to the database
        database.commit()

    # Clean up the database connection
    cur.close()
    database.close()


def get_package_metadata(dependency):
    """
    Retrieve the downloads, categories, and modified date for a package
    """

    version_symbol_index = dependency.rfind('@')
    name_index = dependency.find('/') + 1
    dependency_name = dependency[name_index:version_symbol_index]

    entry = dict()

    entry['name'] = dependency

    result = json.loads(pypistats.recent(dependency_name, "month", format="json"))
    print(result)
    entry['downloads_last_month'] = result['data']['last_month']
    request_url = f'{PYPI_DEPENDENCY_META_URL}{dependency_name}/{dependency[version_symbol_index+1:]}/json'
    json_result = requests.get(request_url)
    print(request_url)
    print(json_result)
    return entry

get_package_metadata('pkg:pypi/gunicorn@0.1')