"""
Fetch package metadata from the conda API
"""

import json
import requests
import datetime
from condastats.cli import overall, pkg_platform, pkg_version, pkg_python, data_source
from psql import connect_to_db, update_package_metadata


def get_package_metadata(dependency):
    """
    Retrieve the downloads, categories, and modified date for a package from conda API
    """

    version_symbol_index = dependency.rfind('@')
    name_index = dependency.find('/') + 1
    dependency_name = dependency[name_index:version_symbol_index]

    entry = dict()
    entry['name'] = dependency

    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    last_month_str = last_month.strftime("%Y-%m")
    result = overall(dependency_name, month=last_month_str)
    try:
        entry['monthly_downloads_last_month'] = result[dependency_name]
    except:
        entry['monthly_downloads_last_month'] = None
    entry['monthly_downloads_a_year_ago'] = None
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
    cur.execute("SELECT name FROM packages WHERE name LIKE 'pkg:pypi/%';")
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

