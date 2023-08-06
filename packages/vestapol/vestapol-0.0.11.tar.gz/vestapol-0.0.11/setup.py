# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vestapol',
 'vestapol.api',
 'vestapol.destinations',
 'vestapol.web_resources',
 'vestapol.writers']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-bigquery>=2.31,<3.0',
 'google-cloud-storage>=1.43,<2.0',
 'pendulum>=2.1,<3.0',
 'requests>=2.26,<3.0']

setup_kwargs = {
    'name': 'vestapol',
    'version': '0.0.11',
    'description': 'Python package that loads data from the web and deploys a corresponding external table definition, so that the data can be queried using standard SQL.',
    'long_description': '# vestapol\n\nvestapol is a Python package that loads data from the web and deploys a corresponding external table definition, so that the data can be queried using standard SQL.\n\n["Vestapol"](https://www.youtube.com/watch?v=SKQG-JGyn7U) is an open D Major tuning for the guitar. It is named after a 19th-century composition distributed in some of the earliest instructional guides for guitar.\n\n## Usage\n\n```python\nfrom vestapol.web_resources.csv_resource import CSVResource\nfrom vestapol.destinations.gcp_destination import GoogleCloudPlatform\n\n\nnyt_covid_data_2022 = CSVResource(\n    name="nyt_covid19_us_counties_2022",\n    base_url="https://raw.githubusercontent.com/",\n    endpoint="nytimes/covid-19-data/master/rolling-averages/us-counties-2022.csv",\n    version="v0",\n    has_header=True,\n)\n\ndestination = GoogleCloudPlatform()\n\nnyt_covid_data_2022.load(destination)\ntablename = destination.create_table(nyt_covid_data_2022)\n\n\nfrom google.cloud import bigquery\n\nclient = bigquery.Client()\nquery = f"""\n    select date, state, county, cases_avg_per_100k\n    from `{tablename}`\n    where requested_at = \'{nyt_covid_data_2022.requested_at}\'\n    limit 5\n"""\nquery_job = client.query(query)\nfor row in query_job.result():\n    print(row)\n```\n\n\n## Prerequisites\n\nInstallation of this project requires [Poetry](https://python-poetry.org/docs/) and Python version 3.8+.\n\n\n## Installation\n\nInstall vestapol and its dependencies by running:\n\n```shell\npoetry install\n```\n\n## Testing\n\nRun tests with the following command:\n\n```shell\npoetry run pytest\n```\n\n## Environment Variables\n\n- `GCS_BUCKET_NAME`: the Google Cloud Storage bucket where data is loaded (e.g. `inq-warehouse-waligob`)\n- `GCS_ROOT_PREFIX`: the GCS prefix where data is loaded (e.g. `data_catalog`)\n- `GBQ_PROJECT_ID`: the BigQuery project identifier (e.g. `inq-warehouse`)\n- `GBQ_DATASET_ID`: the BigQuery dataset where external tables will be created (e.g. `data_catalog_waligob`)\n- `GBQ_DATASET_LOCATION`: the BigQuery dataset location (e.g. `US`)\n- `GOOGLE_APPLICATION_CREDENTIALS=`: location of the GCS service account keyfile (e.g. `~/inq-warehouse-f0962a57089e-inf.json`)\n\n\n## Publishing to PyPI\n\nInstructions for pushing new versions of `vestapol` to PyPI:\n\n1. Update `CHANGELOG.md`. Include Additions, Fixes, and Changes.\n\n2. Update project version using either a valid [PEP 440 string](https://peps.python.org/pep-0440/) or a [valid bump rule](https://python-poetry.org/docs/master/cli/#version) following [Semantic Versioning](http://semver.org/).\n\n```shell\n    poetry version <version string or bump rule>\n```\n\n3. Create a [release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release) and check the CD Pipeline [action](https://github.com/phillymedia/vestapol/actions/workflows/release.yml) to ensure that the project was built and published to PyPI successfully.\n',
    'author': 'Brian Waligorski',
    'author_email': 'bwaligorski@inquirer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/phillymedia/vestapol',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.12,<3.11',
}


setup(**setup_kwargs)
