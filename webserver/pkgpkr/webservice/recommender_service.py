import requests
import random

from pkgpkr.settings import NPM_DEPENDENCY_META_URL, NPM_LAST_MONTH_DOWNLOADS_META_API_URL, NPM_DEPENDENCY_URL


class RecommenderService:

    def __init__(self):

        self.reimport_model_from_s3()

        self.model = None
        pass

    def reimport_model_from_s3(self):

        # TODO connect to S3 and read the file
        # TODO point enpoint at this refre
        # self.model = None
        pass

    def get_average_monthly_donwloads(self, daily_donwloads_list):

        total = 0
        for daily_donwloads in daily_donwloads_list:
            total += daily_donwloads['downloads']

        return total // len(daily_donwloads_list)

    def get_recommendations(self, dependencies):

        # TODO call model
        # self.model.predict(dependencies)

        recommended_dependencies = []

        for dependency in dependencies:

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
