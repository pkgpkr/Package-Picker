import requests
import random
import boto3
import pandas as pd
from io import BytesIO

import psycopg2
import os
import re

from pkgpkr.settings import NPM_DEPENDENCY_META_URL
from pkgpkr.settings import NPM_LAST_MONTH_DOWNLOADS_META_API_URL
from pkgpkr.settings import NPM_DEPENDENCY_URL
from pkgpkr.settings import S3_BUCKET
from pkgpkr.settings import S3_MODEL_PATH
from pkgpkr.settings import S3_ACCESS_KEY_ID
from pkgpkr.settings import S3_SECRET_ACCESS_KEY
from pkgpkr.settings import DB_HOST
from pkgpkr.settings import DB_USER
from pkgpkr.settings import DB_PASSWORD

class RecommenderService:

    def __init__(self):

        self.reimport_model_from_s3()
        self.majorVersionRegex = re.compile(r'pkg:npm/.*@\d+')

    def reimport_model_from_s3(self):

        # Initialize the S3 client
        s3 = boto3.client('s3',
                  aws_access_key_id=S3_ACCESS_KEY_ID,
                  aws_secret_access_key=S3_SECRET_ACCESS_KEY)

        # Connect to S3 and fetch the model file
        obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_MODEL_PATH)
        parquet_bytes = obj['Body'].read()

        # Load it into a Pandas dataframe (requires the `fastparquet` library)
        self.model = pd.read_parquet(BytesIO(parquet_bytes))

    def get_average_monthly_donwloads(self, daily_donwloads_list):

        total = 0
        for daily_donwloads in daily_donwloads_list:
            total += daily_donwloads['downloads']

        return total // len(daily_donwloads_list)

    def get_recommendations(self, dependencies):

        # Connect to our database
        db = psycopg2.connect(f"host={DB_HOST} user={DB_USER} password={DB_PASSWORD}")
        cur = db.cursor()

        # Get recommendations from our model
        recs_per_dep = 10
        recommended = []
        for dependency in dependencies:

            # Strip everything after the major version
            match = self.majorVersionRegex.search(dependency)
            if not match:
                continue
            packageWithMajorVersion = match.group()

            # Get the corresponding ID
            cur.execute(f"SELECT id FROM packages WHERE name = '{packageWithMajorVersion}'")
            result = cur.fetchone()
            if not result:
                continue
            packageId = result[0]

            recommendedIds = self.model[self.model.package_a == packageId].sort_values('similarity', ascending=False)['package_b']
            for identifier in recommendedIds[:recs_per_dep]:
                cur.execute("SELECT name FROM packages WHERE id = " + str(identifier))
                result = cur.fetchone()
                if not result:
                    continue
                recommended.append(result[0])

        # Disconnect from the database
        cur.close()
        db.close()

        # Get metadata for each recommendation
        recommended_dependencies = []
        for dependency in recommended:

            at_split = dependency.split('@')
            dependency_name = at_split[len(at_split)-2].split('/')[len(at_split)-3]

            d = dict()

            d['name'] = dependency

            # Get average downloads
            res = requests.get(NPM_LAST_MONTH_DOWNLOADS_META_API_URL + f'/{dependency_name}')

            # If there are download counts for the package
            if 'downloads' in res.json():
                average_downloads = self.get_average_monthly_donwloads(res.json()['downloads'])
            else:
                average_downloads = 0

            # Commas as thousands separators
            d['average_downloads'] = f'{average_downloads:,}'

            # Get keywords (i.e. categories)
            res = requests.get(NPM_DEPENDENCY_META_URL + f'/{dependency_name}')

            res_json = res.json()

            # Get lastest version
            if 'dist-tags' in res_json:
                dependency_version = res_json['dist-tags']['latest']
            else:
                dependency_version = '0.0.0'

            d['keywords'] = None
            d['date'] = None

            if res_json.get('versions') and \
                    res_json['versions'].get(dependency_version) and \
                    res_json['versions'][dependency_version].get('keywords'):
                d['keywords'] = res_json['versions'][dependency_version]['keywords']

                # Version Date
                dateTime = res_json['time'][dependency_version]

                # Convert time format e.g. 2020-03-16T13:03:34Z -> 2020-03-16 13:03:34
                date = dateTime.split('T')[0]

                d['date'] = date

            # Url to NPM
            d['url'] = NPM_DEPENDENCY_URL + f'/{dependency_name}'

            # TODO placeholder for the rate
            d['rate'] = round(random.uniform(1, 5), 1)

            recommended_dependencies.append(d)

        return recommended_dependencies
