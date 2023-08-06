# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['qlient', 'qlient.http']

package_data = \
{'': ['*']}

install_requires = \
['qlient-core>=1.0.1,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'websocket-client>=1.3.3,<2.0.0']

setup_kwargs = {
    'name': 'qlient',
    'version': '1.0.0',
    'description': 'A fast and modern graphql client designed with simplicity in mind.',
    'long_description': '# Qlient: Python GraphQL Client\n\n[![DeepSource](https://deepsource.io/gh/qlient-org/python-qlient.svg/?label=active+issues&token=2ZJ0b1dinekjVtwgJHSy286C)](https://deepsource.io/gh/qlient-org/python-qlient/?ref=repository-badge)\n[![DeepSource](https://deepsource.io/gh/qlient-org/python-qlient.svg/?label=resolved+issues&token=2ZJ0b1dinekjVtwgJHSy286C)](https://deepsource.io/gh/qlient-org/python-qlient/?ref=repository-badge)\n[![pypi](https://img.shields.io/pypi/v/qlient.svg)](https://pypi.python.org/pypi/qlient)\n[![versions](https://img.shields.io/pypi/pyversions/qlient.svg)](https://github.com/qlient-org/python-qlient)\n[![license](https://img.shields.io/github/license/qlient-org/python-qlient.svg)](https://github.com/qlient-org/python-qlient/blob/master/LICENSE)\n[![codestyle](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)\n\nA fast and modern graphql client designed with simplicity in mind.\n\n## Key Features\n\n* Compatible with Python 3.7 and above\n* Build on top of\n  [qlient-core](https://github.com/qlient-org/python-qlient-core),\n  [requests](https://github.com/psf/requests)\n  and [websocket-client](https://github.com/websocket-client/websocket-client/)\n* support for subscriptions\n\n## Help\n\nSee [documentation](https://qlient-org.github.io/python-qlient/) for more details.\n\nIf you want more information about the internals,\nI kindly refer you to the [qlient-core documentation](https://qlient-org.github.io/python-qlient-core/).\n\nIf you are looking for an asynchronous implementation,\nI kindly refer you to the [qlient-aiohttp](https://github.com/qlient-org/python-qlient-aiohttp) sister project.\n\n## Installation\n\n```shell\npip install qlient\n```\n\n## Quick Start\n\n````python\nfrom qlient.http import HTTPClient, GraphQLResponse\n\nclient = HTTPClient("https://swapi-graphql.netlify.app/.netlify/functions/index")\n\nres: GraphQLResponse = client.query.film(\n    # swapi graphql input fields\n    id="ZmlsbXM6MQ==",\n\n    # qlient specific\n    _fields=["id", "title", "episodeID"]\n)\n\nprint(res.request.query)  # query film($id: ID) { film(id: $id) { id title episodeID } }\nprint(res.request.variables)  # {\'id\': \'ZmlsbXM6MQ==\'}\nprint(res.data)  # {\'film\': {\'id\': \'ZmlsbXM6MQ==\', \'title\': \'A New Hope\', \'episodeID\': 4}}\n````\n',
    'author': 'Daniel Seifert',
    'author_email': 'info@danielseifert.ch',
    'maintainer': 'Daniel Seifert',
    'maintainer_email': 'info@danielseifert.ch',
    'url': 'https://qlient-org.github.io/python-qlient/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
