# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nlhappy',
 'nlhappy.algorithms',
 'nlhappy.callbacks',
 'nlhappy.components',
 'nlhappy.configs',
 'nlhappy.datamodules',
 'nlhappy.layers',
 'nlhappy.layers.attention',
 'nlhappy.layers.classifier',
 'nlhappy.layers.embedding',
 'nlhappy.metrics',
 'nlhappy.models',
 'nlhappy.models.event_extraction',
 'nlhappy.models.language_modeling',
 'nlhappy.models.prompt_relation_extraction',
 'nlhappy.models.prompt_span_extraction',
 'nlhappy.models.relation_extraction',
 'nlhappy.models.span_classification',
 'nlhappy.models.text_classification',
 'nlhappy.models.text_multi_classification',
 'nlhappy.models.text_pair_classification',
 'nlhappy.models.text_pair_regression',
 'nlhappy.models.token_classification',
 'nlhappy.tricks',
 'nlhappy.utils']

package_data = \
{'': ['*'],
 'nlhappy.configs': ['callbacks/*',
                     'datamodule/*',
                     'experiment/*',
                     'log_dir/*',
                     'logger/*',
                     'model/*',
                     'trainer/*']}

install_requires = \
['datasets>=2.0.0,<3.0.0',
 'googletrans==4.0.0rc1',
 'hydra-colorlog==1.1.0',
 'hydra-core==1.1.1',
 'oss2>=2.15.0,<3.0.0',
 'pytorch-lightning>=1.5.10,<2.0.0',
 'rich>=12.4.3,<13.0.0',
 'spacy>=3.3.0',
 'torch>=1.11.0,<2.0.0',
 'transformers>=4.17.0,<5.0.0',
 'wandb>=0.12.18']

entry_points = \
{'console_scripts': ['nlhappy = nlhappy.run:train'],
 'spacy_factories': ['span_classifier = nlhappy.components:make_spancat']}

setup_kwargs = {
    'name': 'nlhappy',
    'version': '2022.8.2',
    'description': '😄让你爱上自然语言处理😄',
    'long_description': None,
    'author': 'wangmengdi',
    'author_email': 'ddream_ai@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
