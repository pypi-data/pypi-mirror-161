# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strawberry_django_plus',
 'strawberry_django_plus.gql',
 'strawberry_django_plus.integrations',
 'strawberry_django_plus.management.commands',
 'strawberry_django_plus.middlewares',
 'strawberry_django_plus.mutations',
 'strawberry_django_plus.test',
 'strawberry_django_plus.utils']

package_data = \
{'': ['*'], 'strawberry_django_plus': ['templates/strawberry_django_plus/*']}

install_requires = \
['django>=3.2',
 'strawberry-graphql-django>=0.4.0',
 'strawberry-graphql>=0.115.0',
 'typing-extensions>=4.2.0']

extras_require = \
{'debug-toolbar': ['django-debug-toolbar>=3.4'],
 'enum': ['django-choices-field>=2.0']}

setup_kwargs = {
    'name': 'strawberry-django-plus',
    'version': '1.22.0',
    'description': 'Enhanced Strawberry GraphQL integration with Django',
    'long_description': "# strawberry-django-plus\n\n[![build status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fblb-ventures%2Fstrawberry-django-plus%2Fbadge%3Fref%3Dmain&style=flat)](https://actions-badge.atrox.dev/blb-ventures/strawberry-django-plus/goto?ref=main)\n[![coverage](https://img.shields.io/codecov/c/github/blb-ventures/strawberry-django-plus.svg)](https://codecov.io/gh/blb-ventures/strawberry-django-plus)\n[![downloads](https://pepy.tech/badge/strawberry-django-plus)](https://pepy.tech/project/strawberry-django-plus)\n[![PyPI version](https://img.shields.io/pypi/v/strawberry-django-plus.svg)](https://pypi.org/project/strawberry-django-plus/)\n![python version](https://img.shields.io/pypi/pyversions/strawberry-django-plus.svg)\n![django version](https://img.shields.io/pypi/djversions/strawberry-django-plus.svg)\n\nEnhanced Strawberry integration with Django.\n\nBuilt on top of [strawberry-django](https://github.com/strawberry-graphql/strawberry-graphql-django)\nintegration, enhancing its overall functionality.\n\nCheck the [docs](https://blb-ventures.github.io/strawberry-django-plus/)\nfor information on how to use this lib.\n\n## Features\n\n- All supported features by `strawberry` and `strawberry-django`, with proper typing and\n  documentation.\n- [Query optimizer extension](https://blb-ventures.github.io/strawberry-django-plus/query-optimizer/)\n  that automatically optimizes querysets\n  (using `only`/`select_related`/`prefetch_related`) to solve graphql `N+1` problems, with support\n  for fragment spread, inline fragments, `@include`/`@skip` directives, prefetch merging, etc\n- [Django choices enums using](https://blb-ventures.github.io/strawberry-django-plus/quickstart/#django-choices-enums)\n  support for better enum typing (requires\n  [django-choices-field](https://github.com/bellini666/django-choices-field))\n- [Permissioned resolvers](https://blb-ventures.github.io/strawberry-django-plus/quickstart/#permissioned-resolvers)\n  using schema directives, supporting both\n  [django authentication system](https://docs.djangoproject.com/en/4.0/topics/auth/default/),\n  direct and per-object permission checking for backends that implement those (e.g.\n  [django-guardian](https://django-guardian.readthedocs.io/en/stable])).\n- [Mutations for Django](https://blb-ventures.github.io/strawberry-django-plus/quickstart/#django-mutations),\n  with CRUD support and automatic errors validation.\n- [Relay support](https://blb-ventures.github.io/strawberry-django-plus/quickstart/#relay-support)\n  for queries, connections and input mutations, all integrated with django types directly.\n- [Django Debug Toolbar integration](https://blb-ventures.github.io/strawberry-django-plus/debug-toolbar/)\n  with graphiql to display metrics like SQL queries\n- Improved sync/async resolver that priorizes the model's cache to avoid have to use\n  [sync_to_async](https://docs.djangoproject.com/en/4.0/topics/async/#asgiref.sync.sync_to_async)\n  when not needed.\n\n## Installation\n\n```shell\npip install strawberry-django-plus\n```\n\n## Licensing\n\nThe code in this project is licensed under MIT license. See [LICENSE](./LICENSE)\nfor more information.\n\n## Stats\n\n![Recent Activity](https://images.repography.com/23718985/blb-ventures/strawberry-django-plus/recent-activity/bf7c25def67510b494ac7981e0f4082c.svg)\n",
    'author': 'Thiago Bellini Ribeiro',
    'author_email': 'thiago@bellini.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/blb-ventures/strawberry-django-plus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
