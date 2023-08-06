# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vdtk',
 'vdtk.metrics.bleu',
 'vdtk.metrics.cider',
 'vdtk.metrics.meteor',
 'vdtk.metrics.rouge',
 'vdtk.metrics.tokenizer']

package_data = \
{'': ['*'], 'vdtk': ['assets/*']}

install_requires = \
['absl-py>=1.0.0,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'fuzzysearch>=0.7.3,<0.8.0',
 'fuzzywuzzy>=0.18.0,<0.19.0',
 'matplotlib>=3.5.0,<4.0.0',
 'mpire>=2.3.1,<3.0.0',
 'msgpack>=1.0.2,<2.0.0',
 'nltk>=3.6.5,<4.0.0',
 'numpy>=1.21.4,<2.0.0',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'rich>=10.14.0,<11.0.0',
 'sentence-transformers>=2.1.0,<3.0.0',
 'spacy>=3.2.0,<4.0.0',
 'textdistance>=4.2.2,<5.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['vdtk-cli = vdtk.cli:cli']}

setup_kwargs = {
    'name': 'vdtk',
    'version': '0.1.0',
    'description': '',
    'long_description': '# vdtk: Visual Description Data Evaluation Tools\n\nThis tool is designed to allow for a deep investigation of diversity in visual description datasets, and to help users\nunderstand their data at a token, n-gram, description, and dataset level.\n\n## Installation\n\nTo use this tool, you can easily pip install with `pip install .` from this directory. Note: Some metrics (METEOR) require\na working installation of Java. Please follow the directions (here) to install the Java runtime if you do not already\nhave access to a JRE.\n\n## Data format\n\nIn order to prepare datasets to work with this tool, datasets must be formatted as JSON files with the following schema\n```json\n// List of samples in the dataset\n[\n    // JSON object for each sample\n    {\n        "_id": "string", // A string ID for each sample. This can help keep track of samples during use.\n        "split": "string", // A string corresponding to the split of the data. Default splits are "train", "validate" and "test"\n        "references": [\n            // List of string references\n            "reference 1...",\n            "reference 2...",\n        ],\n        "metadata": {} // Any JSON object. This field is not used by the toolkit at this time.\n    }\n]\n```\n\n## Usage\n\nAfter installation, the basic menu of commands can be accessed with `vdtk-cli --help`. We make several experiments/tools\navailable for use:\n\n| Command | Details |\n| ----------- | ----------- |\n| vocab-stats | Run with `vdtk-cli vocab-stats DATASET_JSON_PATH`. Compute basic token-level vocab statistics |\n| ngram-stats | Run with `vdtk-cli ngram-stats DATASET_JSON_PATH`. Compute n-gram statistics, EVS@N and ED@N  |\n| caption-stats | Run with `vdtk-cli caption-stats DATASET_JSON_PATH`. Compute caption-level dataset statistics  |\n| semantic-variance | Run with `vdtk-cli semantic-variance DATASET_JSON_PATH`. Compute within-sample BERT embedding semantic variance |\n| coreset | Run with `vdtk-cli coreset DATASET_JSON_PATH`. Compute the caption coreset from the training split needed to solve the validation split |\n| concept-overlap | Run with `vdtk-cli concept-overlap DATASET_JSON_PATH`. Compute the concept overlap between popular feature extractors, and the dataset |\n| concept-leave-one-out | Run with `vdtk-cli concept-leave-one-out DATASET_JSON_PATH`. Compute the performance with a coreset of concept captions |\n| leave-one-out | Run with `vdtk-cli vocab-stats DATASET_JSON_PATH`. Compute leave-one-out ground truth performance on a dataset with multiple ground truths |\n| **[BETA]** balanced-split | Run with `vdtk-cli balanced-split DATASET_JSON_PATH`. Compute a set of splits of the data which best balance the data diversity |\n\nFor more details and options, see the `--help` command for any of the commands above. Note that some tools are relatively\ncompute intensive. This toolkit will make use of a GPU if available and necessary, as well as a large number of CPU cores\nand RAM depending on the task.\n\n**[BETA]** See the [API Docs](https://) for usage as a library.\n',
    'author': 'DavidMChan',
    'author_email': 'davidchan@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CannyLab/vdtk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
