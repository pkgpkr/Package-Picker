"""
Fetch package metadata from the npmjs registry API
"""

import datetime
import requests
import simplejson
from .month_calculation import month_delta
from .psql import connect_to_db, update_package_metadata

NPM_DEPENDENCY_META_URL = 'https://registry.npmjs.org'
NPM_DEPENDENCY_URL = 'https://npmjs.com/package'
NPM_DOWNLOADS_API_URL = 'https://api.npmjs.org/downloads/point'

def get_package_metadata(dependency):
    """
    Retrieve the downloads, categories, and modified date for a package

    arguments:
        :dependency: A specific dependency to fetch metadata for

    returns:
        dict with package metadata (e.g name, categories, modified) 
    """

    version_symbol_index = dependency.rfind('@')
    name_index = dependency.find('/') + 1
    dependency_name = dependency[name_index:version_symbol_index]

    entry = dict()

    entry['name'] = dependency

    # Get downloads
    now = datetime.datetime.now()
    last_month_str = f'{month_delta(now, 1).strftime("%Y-%m-%d")}:{now.strftime("%Y-%m-%d")}'
    month_last_year_str = f'{month_delta(now, 13).strftime("%Y-%m-%d")}:{month_delta(now, 12).strftime("%Y-%m-%d")}'
    entry['monthly_downloads_last_month'] = 0
    entry['monthly_downloads_a_year_ago'] = 0
    try:
        last_month_downloads_json = requests.get(f'{NPM_DOWNLOADS_API_URL}/{last_month_str}/{dependency_name}').json()
        month_last_year_downloads_json = requests.get(f'{NPM_DOWNLOADS_API_URL}/{month_last_year_str}/{dependency_name}').json()

        # Get monthly downloads over the past month
        if last_month_downloads_json.get('downloads'):
            entry['monthly_downloads_last_month'] = last_month_downloads_json['downloads']

        # Get monthly downloads for the month a year ago
        if month_last_year_downloads_json.get('downloads'):
            entry['monthly_downloads_a_year_ago'] = month_last_year_downloads_json['downloads']
    except requests.exceptions.RequestException as exc:
        print(f"Could not request downloads for {dependency_name}: {exc}")
    except simplejson.errors.JSONDecodeError as exc:
        print(f"Could not decode download metadata for {dependency_name}: {exc}")

    # Get keywords (i.e. categories) and date
    entry['categories'] = None
    entry['modified'] = None
    try:
        res_json = requests.get(f'{NPM_DEPENDENCY_META_URL}/{dependency_name}').json()

        if res_json.get('keywords'):
            entry['categories'] = res_json.get('keywords')

        if res_json.get('time') and res_json['time'].get('modified'):
            entry['modified'] = res_json['time']['modified']
    except requests.exceptions.RequestException as exc:
        print(f"Could not request {NPM_DEPENDENCY_META_URL}/{dependency_name}: {exc}")
    except simplejson.errors.JSONDecodeError as exc:
        print(f"Could not decode packument for {dependency_name}: {exc}")

    return entry

def run_query():
    """
    Enrich the package table with metadata for all packages in the table
    """

    # Connect to the database
    database = connect_to_db()
    cur = database.cursor()

    # Fetch all package names from the database
    cur.execute("SELECT name FROM packages WHERE name LIKE 'pkg:npm/%';")
    results = [result[0] for result in cur.fetchall()]

    # Fetch all metadata for the packages from npmjs.com and write to the database
    for result in results:
        print(f"Fetching metadata for {result}")
        metadata = get_package_metadata(result)
        update_package_metadata(database,
                                metadata['name'],
                                metadata['monthly_downloads_last_month'],
                                metadata['monthly_downloads_a_year_ago'],
                                metadata['categories'],
                                metadata['modified'])

        # Commit the changes to the database
        database.commit()

    # Clean up the database connection
    cur.close()
    database.close()
