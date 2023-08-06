# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hoppr_cyclonedx_models',
 'hoppr_cyclonedx_models.cyclonedx_1_3',
 'hoppr_cyclonedx_models.cyclonedx_1_4']

package_data = \
{'': ['*']}

install_requires = \
['datamodel-code-generator>=0.13.0,<0.14.0',
 'pydantic>=1.9.1,<2.0.0',
 'pylint>=2.14.4,<3.0.0',
 'semantic-release>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'hoppr-cyclonedx-models',
    'version': '0.2.1',
    'description': 'CycloneDX Pydantic models for easy use in your Python project.',
    'long_description': '# hoppr_cyclonedx_models\n\n## Purpose\nThe `model-gen.sh` script pulls a user-specified release from the [CycloneDX SBOM Specification](https://github.com/CycloneDX) that operates under the SBOM guidelines.  It then utilizes the [datamodel code generator](https://koxudaxi.github.io/datamodel-code-generator/) to generate Pydantic models from the input SBOM schema file.  These Pydantic models are available as a public package in PyPI under `hoppr_cyclonedx_models`.\n## Usage \n### Install `datamodel-code-generator`:\n-----------------------------------------\n`pip install datamodel-code-generator`\n\nFor further reference see the [documentation](https://koxudaxi.github.io/datamodel-code-generator/).\n\n### Create your model:\n-----------------------------------------\n`./model-gen.sh x.y` \n\nWhere x and y refer to the applicable major and minor revisons respectively.\n\n* Example Usage: `./model-gen.sh 1.4`\n\nTo see all current releases visit [CycloneDX Specification Releases](https://github.com/CycloneDX/specification/releases)',
    'author': 'LMCO Open Source',
    'author_email': 'open.source@lmco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/lmco/hoppr/hoppr-cyclonedx-models',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
