# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['frantic']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-firestore>=2.6.0,<3.0.0', 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'frantic',
    'version': '0.1.0',
    'description': 'Firestore with Pydantic models integration',
    'long_description': '# Frantic\n\nFirestore with Pydantic models integration.\n\nPlease note that this module is a work in progress. API may change over time. Also, the code is not tested yet\nand there are no security checks run periodically.\n\n## Basic usage\n\nIf you have your service account key path set in `GOOGLE_APPLICATION_CREDENTIALS`, it\'s fairly easy:\n\n```python\nimport asyncio\nfrom typing import ClassVar\nfrom frantic import Frantic, BaseModel\n\n\n# Create a model the same way you would do it with Pydantic\nclass User(BaseModel):\n    # optionally, you may specify name of collection instances will be stored within:\n    collection: ClassVar = "my_users_collection"\n    # field \'id\' is added automatically\n    name: str\n\n\nasync def main():\n    frantic = Frantic()\n\n    user = User(name="ijustfarted")\n\n    # Save user in the Firestore db\n    await frantic.add(user)\n\n    # user\'s id gets automatically populated and can be used to retrieve the user\n    retrieved = await frantic.get(User, user.id)\n    assert retrieved.name == user.name\n\n    # list all users\n    users = await frantic.list(User)\n\n    # delete user\n    await frantic.delete(user)\n    # or\n    await frantic.delete(User, user.id)\n\nif __name__ == "__main__":\n    asyncio.run(main)\n```\n',
    'author': 'Tomas Votava',
    'author_email': 'info@tomasvotava.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tomasvotava/frantic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
