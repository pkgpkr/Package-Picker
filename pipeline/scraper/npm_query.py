"""
Fetch package metadata from the npmjs registry API
"""

import datetime
import requests
from month_calculation import month_delta
from psql import connect_to_db, update_package_metadata

NPM_DEPENDENCY_META_URL = 'https://registry.npmjs.org'
NPM_DEPENDENCY_URL = 'https://npmjs.com/package'
NPM_DOWNLOADS_API_URL = 'https://api.npmjs.org/downloads/point'

def get_package_metadata(dependency):
    """
    Retrieve the downloads, categories, and modified date for a package
    """

    version_symbol_index = dependency.rfind('@')
    name_index = dependency.find('/') + 1
    dependency_name = dependency[name_index:version_symbol_index]

    entry = dict()

    entry['name'] = dependency

    # Get downloads
    try:
        now_date = datetime.datetime.now()
        last_month_start = month_delta(now_date, 1).strftime("%Y-%m-%d")
        last_month_end = now_date.strftime("%Y-%m-%d")
        month_last_year_start = month_delta(now_date, 13).strftime("%Y-%m-%d")
        month_last_year_end = month_delta(now_date, 12).strftime("%Y-%m-%d")
        last_month_url = f'{NPM_DOWNLOADS_API_URL}/{last_month_start}:{last_month_end}/{dependency_name}'
        month_last_year_url = f'{NPM_DOWNLOADS_API_URL}/{month_last_year_start}:{month_last_year_end}/{dependency_name}'
        last_month_downloads_json = requests.get(last_month_url).json()
        month_last_year_downloads_json = requests.get(month_last_year_url).json()

        # Get monthly downloads over the past month
        entry['monthly_downloads_last_month'] = 0
        if last_month_downloads_json.get('downloads'):
            entry['monthly_downloads_last_month'] = last_month_downloads_json['downloads']

        # Get monthly downloads for the month a year ago
        entry['monthly_downloads_a_year_ago'] = 0
        if month_last_year_downloads_json.get('downloads'):
            entry['monthly_downloads_a_year_ago'] = month_last_year_downloads_json['downloads']
    except requests.exceptions.RequestException as exc:
        print(f"Could not request downloads for {dependency_name}: {exc}")
        entry['monthly_downloads_last_month'] = 0
        entry['monthly_downloads_a_year_ago'] = 0

    # Get keywords (i.e. categories) and date
    try:
        res = requests.get(f'{NPM_DEPENDENCY_META_URL}/{dependency_name}')
        res_json = res.json()

        entry['categories'] = None
        if res_json.get('keywords'):
            entry['categories'] = res_json.get('keywords')

        entry['modified'] = None
        if res_json.get('time') and res_json['time'].get('modified'):
            entry['modified'] = res_json['time']['modified']
    except requests.exceptions.RequestException as exc:
        print(f"Could not request {NPM_DEPENDENCY_META_URL}/{dependency_name}: {exc}")
        entry['categories'] = None
        entry['modified'] = None

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
