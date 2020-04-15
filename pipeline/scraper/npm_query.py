"""
Fetch package metadata from the npmjs registry API
"""

import requests
from psql import connect_to_db, update_package_metadata

NPM_DEPENDENCY_META_URL = 'https://registry.npmjs.org'
NPM_DEPENDENCY_URL = 'https://npmjs.com/package'
NPM_API_BASE_URL = 'https://api.npmjs.org'
NPM_LAST_MONTH_DOWNLOADS_META_API_URL = f'{NPM_API_BASE_URL}/downloads/range/last-month'

def get_average_monthly_donwloads(daily_donwloads_list):
    """
    Calculate the average monthly downloads from the download API response
    """

    total = 0
    for daily_donwloads in daily_donwloads_list:
        total += daily_donwloads['downloads']

    return total // len(daily_donwloads_list)

def get_package_metadata(dependency):
    """
    Retrieve the downloads, categories, and modified date for a package
    """

    name_index = dependency.find('/') + 1
    dependency_name = dependency[name_index:]

    entry = dict()

    entry['name'] = dependency

    # Get average downloads
    try:
        res = requests.get(f'{NPM_LAST_MONTH_DOWNLOADS_META_API_URL}/{dependency_name}')
        res_json = res.json()

        entry['downloads_last_month'] = 0
        if res_json.get('downloads'):
            downloads_last_month = get_average_monthly_donwloads(res_json.get('downloads'))
            entry['downloads_last_month'] = downloads_last_month
    except requests.exceptions.RequestException as exc:
        print(f"Could not request {NPM_LAST_MONTH_DOWNLOADS_META_API_URL}/{dependency_name}: {exc}")
        entry['downloads_last_month'] = None

    # Get keywords (i.e. categories) and date
    try:
        res = requests.get(f'{NPM_DEPENDENCY_META_URL}/{dependency_name}')
        res_json = res.json()

        entry['categories'] = None
        if res_json.get('keywords'):
            entry['categories'] = res_json.get('keywords')

        entry['modified'] = None
        if res_json.get('time') and res_json.get('time')['modified']:
            entry['modified'] = res_json.get('time')['modified']
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
