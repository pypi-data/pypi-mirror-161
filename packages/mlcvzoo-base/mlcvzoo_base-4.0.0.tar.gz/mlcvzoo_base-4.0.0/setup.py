# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlcvzoo_base',
 'mlcvzoo_base.api',
 'mlcvzoo_base.api.data',
 'mlcvzoo_base.configuration',
 'mlcvzoo_base.data_preparation',
 'mlcvzoo_base.data_preparation.annotation_builder',
 'mlcvzoo_base.data_preparation.annotation_parser',
 'mlcvzoo_base.data_preparation.annotation_writer',
 'mlcvzoo_base.evaluation',
 'mlcvzoo_base.evaluation.object_detection',
 'mlcvzoo_base.metrics',
 'mlcvzoo_base.metrics.mlflow',
 'mlcvzoo_base.models',
 'mlcvzoo_base.models.read_from_file',
 'mlcvzoo_base.third_party',
 'mlcvzoo_base.third_party.efficientdet_pytorch',
 'mlcvzoo_base.third_party.imutils',
 'mlcvzoo_base.third_party.py_faster_rcnn',
 'mlcvzoo_base.utils']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5,<0.6',
 'imageio>=2.9,<3.0',
 'mlflow>=1.22,<2.0',
 'nptyping>=2.0,<3.0',
 'numpy>=1.19.2,!=1.19.5',
 'opencv-contrib-python>=4.5,<5.0,!=4.5.5.64',
 'opencv-python>=4.5,<5.0,!=4.5.5.64',
 'pillow>=8.2,<9.0',
 'protobuf<=3.20',
 'related-mltoolbox>=1.0,<2.0',
 'scikit-learn>=1.0,<2.0',
 'tensorboardX>=2.5,<3.0',
 'terminaltables>=3.1,<4.0',
 'tqdm>=4.61,<5.0',
 'yaml-config-builder>=6.0,<7.0']

extras_require = \
{':python_version < "3.10"': ['backports.strenum>=1.1,<2.0']}

entry_points = \
{'console_scripts': ['mlcvzoo-cvat-handler = '
                     'mlcvzoo_base.tools.cvat_annotation_handler:main',
                     'mlcvzoo-modeltimer = mlcvzoo_base.tools.model_timer:main',
                     'mlcvzoo-preannotator = '
                     'mlcvzoo_base.tools.pre_annotation_tool:main']}

setup_kwargs = {
    'name': 'mlcvzoo-base',
    'version': '4.0.0',
    'description': 'MLCVZoo Base Package',
    'long_description': '# MLCVZoo Base\n\nThe MLCVZoo is an SDK for simplifying the usage of various (machine learning driven)\ncomputer vision algorithms. The package **mlcvzoo_base** provides the base modules\nthat are defining the MLCVZoo API. Furthermore, it includes modules that allow to handle\nand process the data structures of the MLCVZoo, as well as providing modules for\nrunning evaluations / calculation of metrics.\n\nFurther information about the MLCVZoo can be found [here](../README.md).\n\n## Install\n`\npip install mlcvzoo-base\n`\n\n## Technology stack\n\n- Python\n',
    'author': 'Maximilian Otten',
    'author_email': 'maximilian.otten@iml.fraunhofer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.openlogisticsfoundation.org/silicon-economy/base/ml-toolbox/mlcvzoo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
