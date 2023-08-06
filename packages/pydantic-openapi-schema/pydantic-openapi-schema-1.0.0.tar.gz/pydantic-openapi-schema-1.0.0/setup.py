# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_openapi_schema',
 'pydantic_openapi_schema.utils',
 'pydantic_openapi_schema.v3_0_3',
 'pydantic_openapi_schema.v3_1_0']

package_data = \
{'': ['*']}

install_requires = \
['email-validator>=1.2.1,<2.0.0', 'pydantic']

setup_kwargs = {
    'name': 'pydantic-openapi-schema',
    'version': '1.0.0',
    'description': "OpenAPI Schema using pydantic. Forked for Starlite-API from 'openapi-schema-pydantic'.",
    'long_description': None,
    'author': "Na'aman Hirschfeld",
    'author_email': 'nhirschfeld@gmail.com',
    'maintainer': "Na'aman Hirschfeld",
    'maintainer_email': 'nhirschfeld@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
