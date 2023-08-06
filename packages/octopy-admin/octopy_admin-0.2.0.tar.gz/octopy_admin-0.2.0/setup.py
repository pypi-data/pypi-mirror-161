# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['octopy_admin',
 'octopy_admin.graph',
 'octopy_admin.rest',
 'octopy_admin.rest.apis',
 'octopy_admin.rest.apis.actions',
 'octopy_admin.rest.apis.activity',
 'octopy_admin.rest.apis.apps',
 'octopy_admin.rest.apis.billing',
 'octopy_admin.rest.apis.checks',
 'octopy_admin.rest.apis.code_scanning',
 'octopy_admin.rest.apis.codes_of_conduct',
 'octopy_admin.rest.apis.codespaces',
 'octopy_admin.rest.apis.dependabot',
 'octopy_admin.rest.apis.dependency_graph',
 'octopy_admin.rest.apis.emojis',
 'octopy_admin.rest.apis.enterprise_admin',
 'octopy_admin.rest.apis.gists',
 'octopy_admin.rest.apis.git',
 'octopy_admin.rest.apis.gitignore',
 'octopy_admin.rest.apis.interactions',
 'octopy_admin.rest.apis.issues',
 'octopy_admin.rest.apis.licenses',
 'octopy_admin.rest.apis.markdown',
 'octopy_admin.rest.apis.meta',
 'octopy_admin.rest.apis.migrations',
 'octopy_admin.rest.apis.oauth_authorizations',
 'octopy_admin.rest.apis.oidc',
 'octopy_admin.rest.apis.orgs',
 'octopy_admin.rest.apis.packages',
 'octopy_admin.rest.apis.projects',
 'octopy_admin.rest.apis.pulls',
 'octopy_admin.rest.apis.rate_limit',
 'octopy_admin.rest.apis.reactions',
 'octopy_admin.rest.apis.repos',
 'octopy_admin.rest.apis.scim',
 'octopy_admin.rest.apis.search',
 'octopy_admin.rest.apis.secret_scanning',
 'octopy_admin.rest.apis.server_statistics',
 'octopy_admin.rest.apis.teams',
 'octopy_admin.rest.apis.users']

package_data = \
{'': ['*'], 'octopy_admin.graph': ['gql_files/*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'gql>=3.4.0,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'octopy-admin',
    'version': '0.2.0',
    'description': 'octopy_admin is a python library for interacting with the GitHub GraphQL and REST APIs.',
    'long_description': None,
    'author': 'Brett Kuhlman',
    'author_email': 'kuhlman-labs@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
