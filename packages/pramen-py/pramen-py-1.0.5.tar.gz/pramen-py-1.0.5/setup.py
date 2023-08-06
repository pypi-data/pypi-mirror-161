# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pramen_py',
 'pramen_py.app',
 'pramen_py.metastore',
 'pramen_py.models',
 'pramen_py.runner',
 'pramen_py.test_utils',
 'pramen_py.transformation',
 'pramen_py.utils',
 'transformations',
 'transformations.example_trasformation_one',
 'transformations.example_trasformation_two']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['PyYAML>=6.0,<7.0',
 'attrs>=21.4.0,<22.0.0',
 'chispa>=0.9.2,<0.10.0',
 'click>=8.0.3,<9.0.0',
 'contextvars>=2.4,<3.0',
 'environs>=9.5.0,<10.0.0',
 'loguru>=0.6.0,<0.7.0',
 'pyspark-stubs>=3.0.0,<4.0.0',
 'pyspark>=3.0.3,<4.0.0',
 'pytest-asyncio==0.16',
 'pytest-cov==2.12.1',
 'pytest-mock==3.6.1',
 'pytest-sugar>=0.9.4,<0.10.0',
 'pytest==6.2.5',
 'rich>=11.1.0,<12.0.0',
 'types-PyYAML>=6.0.4,<7.0.0',
 'typing-extensions>=4.1.1,<5.0.0']

extras_require = \
{':python_full_version >= "3.6.8" and python_version < "3.7"': ['cattrs==1.0.0'],
 ':python_version >= "3.7" and python_version < "4.0"': ['cattrs>=22.1.0,<23.0.0']}

entry_points = \
{'console_scripts': ['pramen-py = pramen_py.app.cli:main'],
 'pytest11': ['pramen_py = pramen_py.test_utils.plugin']}

setup_kwargs = {
    'name': 'pramen-py',
    'version': '1.0.5',
    'description': 'Pramen transformations written in python',
    'long_description': '# Pramen-py\n\nCli application for defining the data transformations for Pramen.\n\nSee:\n```bash\npramen-py --help\n```\nfor more information.\n\n\n## Installation\n\n### App settings\n\nApplication configuration solved by the environment variables\n(see .env.example)\n\n### Add pramen-py as a dependency to your project\n\nIn case of poetry:\n\n```bash\n# ensure we have valid poetry environment\nls pyproject.toml || poetry init\n\npoetry add pramen-py\n```\nIn case of pip:\n\n```bash\npip install pramen-py\n```\n\n\n## Usage\n\n## Application configuration\n\nIn order to configure the pramen-py options you need to set\ncorresponding environment variables. To see the list of available options run:\n\n```bash\npramen-py list-configuration-options\n```\n\n### Developing transformations\n\npramen-py uses python\'s\n[namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/#native-namespace-packages)\nfor discovery of the transformations.\n\nThis mean, that in order to build a new transformer, it should be located\ninside a python package with the `transformations` directory inside.\n\nThis directory should be declared as a package:\n- for poetry\n```toml\n[tool.poetry]\n# ...\npackages = [\n    { include = "transformations" },\n]\n\n```\n- for setup.py\n```python\nfrom setuptools import setup, find_namespace_packages\n\nsetup(\n    name=\'mynamespace-subpackage-a\',\n    # ...\n    packages=find_namespace_packages(include=[\'transformations.*\'])\n)\n```\n\nExample files structure:\n```\n❯ tree .\n.\n├── README.md\n├── poetry.lock\n├── pyproject.toml\n├── tests\n│  └── test_identity_transformer.py\n└── transformations\n    └── identity_transformer\n        ├── __init__.py\n        └── example_config.yaml\n```\n\nIn order to make transformer picked up by the pramen-py the following\nconditions should be satisfied:\n- python package containing the transformers should be installed to the\nsame python environment as pramen-py\n- python package should have defined namespace package `transformations`\n- transformers should extend `pramen_py.Transformation` base class\n\nSubclasses created by extending Transformation base class are registered as\na cli command (pramen-py transformations run TransformationSubclassName)\nwith default options. Check:\n\n```bash\npramen-py transformations run ExampleTransformation1 --help\n```\n\nfor more details.\n\nYou can add your own cli options to your transformations. See example at\n[ExampleTransformation2](transformations/example_trasformation_two/some_transformation.py)\n\n### pramen-py pytest plugin\n\npramen-py also provides pytest plugin with helpful\nfixtures to test created transformers.\n\nList of available fixtures:\n```bash\n#install pramen-py into the environment and activate it\npytest --fixtures\n# check under --- fixtures defined from pramen_py.test_utils.fixtures ---\n```\n\npramen-py pytest plugin also loads environment variables from .env\nfile if it is presented in the root of the repo.\n\n### Running and configuring transformations\n\nTransformations can be run with the following command:\n```bash\npramen-py transformations run \\\n  ExampleTransformation1 \\\n  --config config.yml \\\n  --info-date 2022-04-01\n```\n\n`--config` is required option for any transformation. See\n[config_example.yaml](tests/resources/real_config.yaml) for more information.\n\nTo check available options and documentation for a particular transformation,\nrun:\n```bash\npramen-py transformations run TransformationClassName --help\n```\nwhere TransformationClassName is the name of the transformation.\n\n## Development\n\nPrerequisites:\n- <https://python-poetry.org/docs/#installation>\n- python 3.6\n\nSetup steps:\n\n```bash\ngit clone https://github.com/AbsaOSS/pramen\ncd pramen-py\nmake install  # create virtualenv and install dependencies\nmake test\nmake pre-commit\n\n# enable completions\n# source <(pramen-py completions zsh)\n# source <(pramen-py completions bash)\n\npramen-py --help\n```\n\n\n### Load environment configuration\n\nBefore doing any development step, you have to set your development\nenvironment variables\n\n```bash\nmake install\n```\n\n## Completions\n\n```bash\n# enable completions\nsource <(pramen-py completions zsh)\n# or for bash\n# source <(pramen-py completions bash)\n```\n\n\n## Deployment\n\n### From the local development environment\n\n```bash\n# bump the version\nvim pyproject.toml\n\n# deploy to the dev environment (included steps of building and publishing\n#   artefacts)\ncat .env.ci\nmake publish\n```\n',
    'author': 'Artem Zhukov',
    'author_email': 'iam@zhukovgreen.pro',
    'maintainer': 'Artem Zhukov',
    'maintainer_email': 'iam@zhukovgreen.pro',
    'url': 'https://github.com/AbsaOSS/pramen',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.8,<4.0',
}


setup(**setup_kwargs)
