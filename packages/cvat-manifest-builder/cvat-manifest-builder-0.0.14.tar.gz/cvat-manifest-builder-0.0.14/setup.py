# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cvat_manifest_builder']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0', 'beartype>=0.10.4,<0.11.0', 'loguru>=0.6.0,<0.7.0']

entry_points = \
{'console_scripts': ['cvat-manifest-builder = '
                     'cvat_manifest_builder.cvat_manifest_builder:app']}

setup_kwargs = {
    'name': 'cvat-manifest-builder',
    'version': '0.0.14',
    'description': 'Builds a CVAT manifest file from a directory of images.',
    'long_description': '# cvat-manifest-builder\n## Installation & Use\n\n```shell\n# Install cvat-manifest-builder\n> pip install cvat-manifest-builder\n\n> cvat-manifest-builder --help\nusage: cvat-manifest-builder [-h] --output_manifest_file OUTPUT_MANIFEST_FILE --input_data_path\n                             INPUT_DATA_PATH\n\nBuilds a CVAT manifest file from a directory of images.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --output_manifest_file OUTPUT_MANIFEST_FILE\n                        Path to the output manifest file.\n  --input_data_path INPUT_DATA_PATH\n                        Path to the data directory.\n```',
    'author': 'Michael Mohamed',
    'author_email': 'michael@foundationstack.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsai-dev/fsai-cli-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
