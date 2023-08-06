# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['harborapi', 'harborapi.models']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=2.1.2,<3.0.0',
 'httpx>=0.23.0,<0.24.0',
 'loguru>=0.6.0,<0.7.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'harborapi',
    'version': '0.1.4',
    'description': 'Async Harbor API v2.0 wrapper',
    'long_description': '# Harbor API\n\nPython async API wrapper for the Harbor  REST API v2.0.\n\n## Features\n\n- Async API\n- Fully typed\n- Data validation with [Pydantic](https://pydantic-docs.helpmanual.io/)\n- HTTP handled by [HTTPX](https://www.python-httpx.org/)\n- Extensive test coverage powered by [Hypothesis](https://hypothesis.works/)\n\n## Installation\n\n```bash\npip install harborapi\n```\n\n## Documentation\n\nDocumentation is available [here](https://pederhan.github.io/harborapi/)\n\n## Implemented endpoints\n\n<!-- - [ ] Products\n- [ ] Chart Repository\n- [ ] Label -->\n- [x] user\n- [x] gc\n- [x] scanAll\n- [x] configure\n- [x] usergroup\n- [ ] preheat\n- [ ] replication\n- [ ] label\n- [x] robot\n- [ ] webhookjob\n- [ ] icon\n- [x] project\n- [ ] webhook\n- [x] scan\n- [ ] member\n- [ ] ldap\n- [x] registry\n- [x] search\n- [x] artifact\n- [ ] immutable\n- [ ] retention\n- [x] scanner\n- [x] systeminfo**\n- [x] statistic\n- [x] quota\n- [x] repository\n- [x] ping\n- [x] oidc\n- [x] SystemCVEAllowlist\n- [x] Health\n- [ ] robotv1\n- [ ] projectMetadata\n- [x] auditlog\n\n\\*\\* `/systeminfo/getcert` NYI\n',
    'author': 'Peder Hovdan Andresen',
    'author_email': 'pederhan@usit.uio.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
