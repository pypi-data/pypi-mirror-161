# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['picsellia_connexion_services']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'picsellia-connexion-services',
    'version': '0.1.0',
    'description': 'Package for connection to Picsellia platforms with some wrapper around requests library',
    'long_description': '# Picsellia Services\n\nPicsellia Services is a Python library that wraps connexions with Picsellia micro services.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install picsellia-connexion-services.\n\n```bash\npip install picsellia-connexion-services\n```\n\n## Usage\n### JwtToken\n```python\nfrom picsellia_connexion_services.jwt_service import JwtServiceConnexion\nservice = JwtServiceConnexion({\'api_token\': \'<api_token>\', \'deployment_id\': \'<deployment_id>\'}, \'localhost:8000\')\nservice.get(\'/deployment/{}/stats\'.format(deployment_id))\n```\n\n## Usage in mocked tests\n\n```python\nfrom picsellia_connexion_services.mocked_service import MockedServiceConnexion\nservice = MockedServiceConnexion(\'test\')\nservice.set_next_mocked_response("get", "/ping", JsonResponse({"ok" : True}, status=status.HTTP_200_OK))\nservice.get("/ping")\n```\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'Thomas Darget',
    'author_email': 'thomasdarget@hotmail.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
