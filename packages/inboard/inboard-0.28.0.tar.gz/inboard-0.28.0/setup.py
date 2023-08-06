# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inboard', 'inboard.app']

package_data = \
{'': ['*']}

install_requires = \
['gunicorn>=20,<21', 'uvicorn[standard]>=0.17,<0.18']

extras_require = \
{'all': ['fastapi>=0.79,<0.80'],
 'fastapi': ['fastapi>=0.79,<0.80'],
 'starlette': ['starlette>=0.19,<0.20']}

setup_kwargs = {
    'name': 'inboard',
    'version': '0.28.0',
    'description': 'Docker images and utilities to power your Python APIs and help you ship faster.',
    'long_description': '# 🚢 inboard 🐳\n\n<img src="https://raw.githubusercontent.com/br3ndonland/inboard/develop/docs/assets/images/inboard-logo.svg" alt="inboard logo" width="90%" />\n\n_Docker images and utilities to power your Python APIs and help you ship faster._\n\n[![PyPI](https://img.shields.io/pypi/v/inboard?color=success)](https://pypi.org/project/inboard/)\n[![GitHub Container Registry](https://img.shields.io/badge/github%20container%20registry-inboard-success)](https://github.com/br3ndonland/inboard/pkgs/container/inboard)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)\n[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=pytest&logoColor=white)](https://coverage.readthedocs.io/en/latest/)\n[![builds](https://github.com/br3ndonland/inboard/workflows/builds/badge.svg)](https://github.com/br3ndonland/inboard/actions)\n\n[![Mentioned in Awesome FastAPI](https://awesome.re/mentioned-badge-flat.svg)](https://github.com/mjhea0/awesome-fastapi)\n\n## Description\n\nThis repository provides [Docker images](https://github.com/br3ndonland/inboard/pkgs/container/inboard) and a [PyPI package](https://pypi.org/project/inboard/) with useful utilities for Python web servers. It runs [Uvicorn with Gunicorn](https://www.uvicorn.org/), and can be used to build applications with [Starlette](https://www.starlette.io/) and [FastAPI](https://fastapi.tiangolo.com/).\n\n## Quickstart\n\n[Get started with Docker](https://www.docker.com/get-started), pull and run an image, and try an API endpoint.\n\n```sh\ndocker pull ghcr.io/br3ndonland/inboard\ndocker run -d -p 80:80 ghcr.io/br3ndonland/inboard\nhttp :80  # HTTPie: https://httpie.io/\n```\n\n## Documentation\n\nDocumentation is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), deployed on [Vercel](https://vercel.com/), and available at [inboard.bws.bio](https://inboard.bws.bio) and [inboard.vercel.app](https://inboard.vercel.app).\n\n[Vercel build configuration](https://vercel.com/docs/build-step):\n\n- Build command: `python3 -m pip install \'mkdocs-material>=8,<9\' && mkdocs build --site-dir public`\n- Output directory: `public` (default)\n\n[Vercel site configuration](https://vercel.com/docs/configuration) is specified in _vercel.json_.\n',
    'author': 'Brendon Smith',
    'author_email': 'bws@bws.bio',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/br3ndonland/inboard',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
