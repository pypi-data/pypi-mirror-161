# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_mvc',
 'fastapi_mvc.cli',
 'fastapi_mvc.commands',
 'fastapi_mvc.generators',
 'fastapi_mvc.generators.controller',
 'fastapi_mvc.generators.controller.template.hooks',
 'fastapi_mvc.generators.controller.template.{{cookiecutter.folder_name}}.tests.unit.app.controllers',
 'fastapi_mvc.generators.controller.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app.controllers',
 'fastapi_mvc.generators.generator',
 'fastapi_mvc.generators.generator.template.hooks',
 'fastapi_mvc.generators.generator.template.{{cookiecutter.folder_name}}.lib.generators.{{cookiecutter.generator_name}}',
 'fastapi_mvc.generators.project',
 'fastapi_mvc.generators.project.template.hooks',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.docs',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.integration',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.app',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.app.controllers',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.app.exceptions',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.app.models',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.app.utils',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.app.views',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.tests.unit.cli',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app.controllers',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app.exceptions',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app.models',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app.utils',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.app.views',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.cli',
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.{{cookiecutter.package_name}}.config',
 'fastapi_mvc.parsers',
 'fastapi_mvc.utils']

package_data = \
{'': ['*'],
 'fastapi_mvc.generators.controller': ['template/*'],
 'fastapi_mvc.generators.generator': ['template/*'],
 'fastapi_mvc.generators.generator.template.{{cookiecutter.folder_name}}.lib.generators.{{cookiecutter.generator_name}}': ['template/*'],
 'fastapi_mvc.generators.project': ['template/*',
                                    'template/{{cookiecutter.folder_name}}/*',
                                    'template/{{cookiecutter.folder_name}}/.github/workflows/*',
                                    'template/{{cookiecutter.folder_name}}/build/*',
                                    'template/{{cookiecutter.folder_name}}/charts/{{cookiecutter.chart_name}}/*',
                                    'template/{{cookiecutter.folder_name}}/charts/{{cookiecutter.chart_name}}/templates/*',
                                    'template/{{cookiecutter.folder_name}}/charts/{{cookiecutter.chart_name}}/templates/tests/*',
                                    'template/{{cookiecutter.folder_name}}/manifests/*'],
 'fastapi_mvc.generators.project.template.{{cookiecutter.folder_name}}.docs': ['_static/*']}

install_requires = \
['click>=8.1.3,<8.2.0', 'cookiecutter>=2.1.1,<2.2.0']

entry_points = \
{'console_scripts': ['fastapi-mvc = fastapi_mvc.cli.cli:cli']}

setup_kwargs = {
    'name': 'fastapi-mvc',
    'version': '0.14.0',
    'description': 'Developer productivity tool for making high-quality FastAPI production-ready APIs.',
    'long_description': '<div align="center">\n\n![fastapi-mvc](https://github.com/rszamszur/fastapi-mvc-template/blob/master/docs/_static/logo.png?raw=true)\n\n![fastapi-mvc](https://github.com/rszamszur/fastapi-mvc-template/blob/master/docs/_static/readme.gif?raw=true)\n[![CI](https://github.com/rszamszur/fastapi-mvc/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/rszamszur/fastapi-mvc/actions/workflows/main.yml)\n[![codecov](https://codecov.io/gh/rszamszur/fastapi-mvc/branch/master/graph/badge.svg?token=7ESV30TYZS)](https://codecov.io/gh/rszamszur/fastapi-mvc)\n[![K8s integration](https://github.com/rszamszur/fastapi-mvc/actions/workflows/integration.yml/badge.svg)](https://github.com/rszamszur/fastapi-mvc/actions/workflows/integration.yml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![PyPI](https://img.shields.io/pypi/v/fastapi-mvc)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/fastapi-mvc)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-mvc)\n![GitHub](https://img.shields.io/github/license/rszamszur/fastapi-mvc?color=blue)\n\n</div>\n\n---\n\n**Documentation**: [https://fastapi-mvc.netlify.app](https://fastapi-mvc.netlify.app)\n\n**Source Code**: [https://github.com/rszamszur/fastapi-mvc](https://github.com/rszamszur/fastapi-mvc)\n\n**Example generated project**: [https://github.com/rszamszur/fastapi-mvc-example](https://github.com/rszamszur/fastapi-mvc-example)\n\n---\n\nFastapi-mvc is a developer productivity tool for FastAPI web framework. \nIt is designed to make programming FastAPI applications easier by making assumptions about what every developer needs to get started. \nIt allows you to write less code while accomplishing more. Core features:\n\n* Generated project Based on MVC architectural pattern\n* WSGI + ASGI production server\n* Generated project comes with Sphinx documentation and 100% unit tests coverage\n* Kubernetes deployment with Redis HA cluster\n* Makefile, GitHub actions and utilities\n* Helm chart for Kubernetes deployment\n* Dockerfile with K8s and cloud in mind\n* Generate pieces of code or even your own generators\n* Uses Poetry dependency management\n* Reproducible development environment using Vagrant or Nix\n\nFastapi-mvc comes with a number of scripts called generators that are designed to make your development life easier by \ncreating everything that’s necessary to start working on a particular task. One of these is the new application generator, \nwhich will provide you with the foundation of a fresh FastAPI application so that you don’t have to write it yourself.\n\nCreating a new project is as easy as:\n\n```shell\n$ fastapi-mvc new /tmp/galactic-empire\n```\n\nThis will create a fastapi-mvc project called galactic-empire in a `/tmp/galactic-empire` directory and install its dependencies using `make install`.\n\nOnce project is generated and installed lets run development uvicorn server (ASGI):\n\n```shell\n$ cd /tmp/galactic-empire\n$ fastapi-mvc run\n[INFO] Executing shell command: [\'/home/demo/.poetry/bin/poetry\', \'install\', \'--no-interaction\']\n    Installing dependencies from lock file\n    \n    No dependencies to install or update\n    \n    Installing the current project: galactic-empire (0.1.0)\n[INFO] Executing shell command: [\'/home/demo/.poetry/bin/poetry\', \'run\', \'uvicorn\', \'--host\', \'127.0.0.1\', \'--port\', \'8000\', \'--reload\', \'galactic_empire.app.asgi:application\']\nINFO:     Will watch for changes in these directories: [\'/tmp/galactic-empire\']\nINFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\nINFO:     Started reloader process [4713] using watchgod\nINFO:     Started server process [4716]\nINFO:     Waiting for application startup.\nINFO:     Application startup complete.\n```\n\nTo confirm it’s actually working:\n\n```shell\n$ curl 127.0.0.1:8000/api/ready\n{"status":"ok"}\n```\n\nNow let\'s add new API endpoints. For that we need to generate new controller:\n\n```shell\n$ fastapi-mvc generate controller death_star status load:post fire:delete\n```\n\nAnd then test generated controller endpoints:\n\n```shell\n$ curl 127.0.0.1:8000/api/death_star/status\n{"hello":"world"}\n$ curl -X POST 127.0.0.1:8000/api/death_star/load\n{"hello":"world"}\n$ curl -X DELETE 127.0.0.1:8000/api/death_star/fire\n{"hello":"world"}\n```\n\nYou will see it working in server logs as well:\n\n```shell\nINFO:     127.0.0.1:47284 - "GET /api/ready HTTP/1.1" 200 OK\nINFO:     127.0.0.1:55648 - "GET /api/death_star/status HTTP/1.1" 200 OK\nINFO:     127.0.0.1:55650 - "POST /api/death_star/load HTTP/1.1" 200 OK\nINFO:     127.0.0.1:55652 - "DELETE /api/death_star/fire HTTP/1.1" 200 OK\n```\n\nYou can get the project directly from PyPI:\n\n```shell\npip install fastapi-mvc\n```\n\n## Projects created with fastapi-mvc\n\nIf you have created a project with fastapi-mvc, feel free to open PR and add yourself to the list. Share your story and project. Your success is my success :)\n\nProjects:\n* [fastapi-mvc-example](https://github.com/rszamszur/fastapi-mvc-example) - Default generated project by `fastapi-mvc new ...`\n\n## Contributing\n\n[CONTRIBUTING](https://github.com/rszamszur/fastapi-mvc/blob/master/CONTRIBUTING.md)\n\n## License\n\n[MIT](https://github.com/rszamszur/fastapi-mvc/blob/master/LICENSE)\n',
    'author': 'Radosław Szamszur',
    'author_email': 'radoslawszamszur@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rszamszur/fastapi-mvc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
