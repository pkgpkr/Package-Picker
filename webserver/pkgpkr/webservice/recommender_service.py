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
            # commas as thousands separators
            d['average_downloads'] = f'{average_downloads:,}'

            # Get keywords (i.e. categories) and date
            res = requests.get(NPM_DEPENDENCY_META_URL + f'/{dependency_name}')

            res_json = res.json()

            d['keywords'] = None
            d['date'] = None

            if res_json.get('versions') and \
                    res_json['versions'].get(dependency_version) and \
                    res_json['versions'][dependency_version].get('keywords'):
                d['keywords'] = res_json['versions'][dependency_version]['keywords']

                # Version Date
                dateTime = res_json['time'][dependency_version]

                # Convert time format e.g. 2017-02-16T20:43:07.414Z -> 2017-02-16 20:43:07
                date = dateTime.split('T')[0]
                timeWithZone = dateTime.split('T')[-1]
                time = timeWithZone.split('.')[0]

                d['date'] = date + ' ' + time

            # Url to NPM
            d['url'] = NPM_DEPENDENCY_URL + f'/{dependency_name}'

            # TODO placeholder for the rate
            d['rate'] = round(random.uniform(1, 5), 1)

            recommended_dependencies.append(d)

        return recommended_dependencies
