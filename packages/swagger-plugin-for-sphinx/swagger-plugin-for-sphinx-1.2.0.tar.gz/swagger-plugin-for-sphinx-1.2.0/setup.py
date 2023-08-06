# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['swagger_plugin_for_sphinx']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=3.0,<4.0', 'sphinx>=4,<6']

setup_kwargs = {
    'name': 'swagger-plugin-for-sphinx',
    'version': '1.2.0',
    'description': 'Sphinx plugin which renders a OpenAPI specification with Swagger',
    'long_description': '[![REUSE status](https://api.reuse.software/badge/github.com/SAP/swagger-plugin-for-sphinx)](https://api.reuse.software/info/github.com/SAP/swagger-plugin-for-sphinx)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# Swagger Plugin for Sphinx\n\nThis is handy plugin to bring [Swagger](https://swagger.io/) and [Sphinx](https://www.sphinx-doc.org/en/master/) together.\n\nIt is able to generate one or multiple swagger HTML pages with a custom configuration which host an OpenAPI specification.\n\n## Install\n\nJust run `pip install swagger-plugin-for-sphinx`\n\n\n## Usage\n\nFirst, add the plugin to the extensions list:\n```python\nextensions = ["swagger_plugin_for_sphinx.plugin"]\n```\n\nThen add the main configuration for swagger:\n```python\nswagger_present_uri = ""\nswagger_bundle_uri = ""\nswagger_css_uri = ""\n```\nThese correspond to the modules explained [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/installation.md).\nBy default the latest release is used from [here](https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest).\n\nAs a last step, define the swagger configuration as followed:\n```python\nswagger = [\n    {\n        "name": "Service API",\n        "page": "openapi",\n        "options": {\n            "url": "openapi.yaml",\n        },\n    }\n]\n```\nEach item of the list will generate a new swagger HTML page.\nThe `name` is the HTML page name and `page` defines the file name without an extension. This needs to be included in the TOC.\nThe `options` are then used for the `SwaggerUIBundle` as defined [here](https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md).\nPlease don\'t specify the `dom_id` since it\'s hardcoded in the HTML page.\n\nIn the sphinx build, a HTML page is created and put into the `_static` directory of the build.\n\nIf the specification is provided as a file, don\'t forget to copy it (e.g. by putting it into the `html_static_path`).\n\nTo silence the warning `toctree contains reference to nonexisting document`,, just put a dummy file with the same name as `page` into the source folder.\n\n## Build and Publish\n\nThis project uses `poetry` as the dependency management and build tool.\nTo publish a new release, follow these steps:\n* Update the version in the `pyproject.toml`\n* Add an entry in the changelog\n* Push a new tag like `vX.X.X` to trigger the release\n\n## Support, Feedback, Contributing\n\nThis project is open to feature requests/suggestions, bug reports etc. via [GitHub issues](https://github.com/SAP/<your-project>/issues). Contribution and feedback are encouraged and always welcome. For more information about how to contribute, the project structure, as well as additional contribution information, see our [Contribution Guidelines](CONTRIBUTING.md).\n\n## Code of Conduct\n\nWe as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone. By participating in this project, you agree to abide by its [Code of Conduct](CODE_OF_CONDUCT.md) at all times.\n\n## Licensing\n\nCopyright 2022 SAP SE or an SAP affiliate company and swagger-plugin-for-sphinx contributors.\nPlease see our [LICENSE](LICENSE) for copyright and license information.\nDetailed information including third-party components and their licensing/copyright information is available [via the REUSE tool](https://api.reuse.software/info/github.com/SAP/<your-project>).\n',
    'author': 'Kai Mueller',
    'author_email': 'kai.mueller01@sap.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/SAP/swagger-plugin-for-sphinx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0',
}


setup(**setup_kwargs)
