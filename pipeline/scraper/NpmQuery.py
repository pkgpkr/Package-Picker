
import requests
import PSQL

NPM_DEPENDENCY_META_URL = 'https://registry.npmjs.org'
NPM_DEPENDENCY_URL = 'https://npmjs.com/package'
NPM_API_BASE_URL = 'https://api.npmjs.org'
NPM_LAST_MONTH_DOWNLOADS_META_API_URL = f'{NPM_API_BASE_URL}/downloads/range/last-month'

def get_average_monthly_donwloads(daily_donwloads_list):

    total = 0
    for daily_donwloads in daily_donwloads_list:
        total += daily_donwloads['downloads']

    return total // len(daily_donwloads_list)

def get_package_metadata(dependency):

    versionSymbolIndex = dependency.rfind('@')
    nameIndex = dependency.find('/') + 1
    dependency_name = dependency[nameIndex:versionSymbolIndex]

    d = dict()

    d['name'] = dependency

    # Get average downloads
    res = requests.get(NPM_LAST_MONTH_DOWNLOADS_META_API_URL + f'/{dependency_name}')
    res_json = res.json()

    d['downloads_last_month'] = 0
    if (res_json.get('downloads')):
        downloads_last_month = get_average_monthly_donwloads(res_json.get('downloads'))
        d['downloads_last_month'] = downloads_last_month

    # Get keywords (i.e. categories) and date
    res = requests.get(NPM_DEPENDENCY_META_URL + f'/{dependency_name}')
    res_json = res.json()

    d['categories'] = None
    if res_json.get('keywords'):
        d['categories'] = res_json.get('keywords')

    d['modified'] = None
    if res_json.get('time') and res_json.get('time')['modified']:
        d['modified'] = res_json.get('time')['modified']

    return d

def runQuery():

    # Connect to the database
    db = connectToDB()
    cur = db.cursor()

    # Fetch all package names from the database
    cur.execute("SELECT name FROM packages;")
    results = [result[0] for result in cur.fetchall()]

    # Fetch all metadata for the packages from npmjs.com and write to the database
    for result in results:
        print(f"Fetching metadata for {result}")
        metadata = get_package_metadata(result)
        updatePackageMetadata(db, metadata['name'], metadata['downloads_last_month'], metadata['categories'], metadata['modified'])

        # Commit the changes to the database
        db.commit()

    # Clean up the database connection
    cur.close()
    db.close()
