import requests
import random
import boto3
import pandas as pd
from io import BytesIO

import psycopg2
import os

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
        recs_per_dep = 2
        recommended = []
        for dependency in dependencies:

            # Get the corresponding ID
            cur.execute(f"SELECT id FROM packages WHERE name = '{dependency}'")
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
            dependency_name = at_split[0].split('/')[-1]
            dependency_version = at_split[-1]

            d = dict()

            d['name'] = dependency

            # Get average downloads
            res = requests.get(NPM_LAST_MONTH_DOWNLOADS_META_API_URL + f'/{dependency_name}')
            average_downloads = self.get_average_monthly_donwloads(res.json()['downloads'])
            d['average_downloads'] = average_downloads

            # Get keywords (i.e. categories)
            res = requests.get(NPM_DEPENDENCY_META_URL + f'/{dependency_name}')

            res_json = res.json()

            d['keywords'] = None

            if res_json.get('versions') and \
                    res_json['versions'].get(dependency_version) and \
                    res_json['versions'][dependency_version].get('keywords'):
                d['keywords'] = res_json['versions'][dependency_version]['keywords']

            # Url to NPM
            d['url'] = NPM_DEPENDENCY_URL + f'/{dependency_name}'

            # TODO placeholder for the rate
            d['rate'] = random.uniform(1, 5)

            recommended_dependencies.append(d)

        return recommended_dependencies
