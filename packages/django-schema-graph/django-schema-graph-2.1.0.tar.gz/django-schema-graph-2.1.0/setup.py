# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['schema_graph']

package_data = \
{'': ['*'],
 'schema_graph': ['static/schema_graph/*', 'templates/schema_graph/*']}

install_requires = \
['attrs']

setup_kwargs = {
    'name': 'django-schema-graph',
    'version': '2.1.0',
    'description': 'An interactive graph of your Django model structure.',
    'long_description': '# Django Schema Graph\n\nDjango-schema-graph makes a colourful diagram out of your Django models. The\ndiagram is interactive, and makes it easy to toggle models and apps on/off at\nwill.\n\nIt looks like this:\n\n| Feature       | Screenshot |\n| ---           | --- |\n| Models        | ![models screenshot](docs-images/models.png) |\n| Apps          | ![apps screenshot](docs-images/apps.png) |\n| Both together | ![models and apps screenshot](docs-images/combination.png) |\n| Graph editor  | ![menu screenshot](docs-images/menu.png) |\n\n(Apologies that the images above don\'t work on PyPI. [Check it out on\nGitHub](https://github.com/meshy/django-schema-graph/blob/master/README.md).)\n\n\n## Installation\n\nInstall from PyPI:\n\n```bash\npip install django-schema-graph\n```\n\nAdd to `INSTALLED_APPS`:\n\n```python\nINSTALLED_APPS = [\n    ...\n    \'schema_graph\',\n    ...\n]\n```\n\nAdd to your URLs.\n\n```python\nfrom schema_graph.views import Schema\nurlpatterns += [\n    # On Django 2+:\n    path("schema/", Schema.as_view()),\n    # Or, on Django < 2:\n    url(r"^schema/$", Schema.as_view()),\n]\n```\n\n## Use\n\nBrowse to `/schema/` (assuming that\'s where you put it in your URLs).\n\nYou can control access to this page using the `SCHEMA_GRAPH_VISIBLE` setting,\nor by subclassing `schema_graph.views.Schema` and overriding `access_permitted`.\nBy default the page is only visible when `DEBUG` is `True`,\nbecause we assume that you don\'t want to leak sensitive information about your\nwebsite outside of local development.\n\n## Support\n\nTests run on sensible combinations of:\n- Python (3.6-3.10)\n- Django (1.11-4.0)\n\nIf you\'re stuck on old version of Python or Django, you may consider installing\nold versions.\nThey will probably have fewer features, and there will be no support for them.\n\nThe last version to support Python 2.7 and 3.5 was 1.2.0\n\nThe last version to support Django 1.8 was 1.2.0\n\n## Alternatives\n\n- [`django-spaghetti-and-meatballs`](https://github.com/LegoStormtroopr/django-spaghetti-and-meatballs)\n  is great. At the time of writing, it offers a lot more detailed information\n  on the models in the diagram, but doesn\'t allow them to be turned on/off in\n  the page.\n',
    'author': 'Charlie Denton',
    'author_email': 'charlie@meshy.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/meshy/django-schema-graph',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.11',
}


setup(**setup_kwargs)
