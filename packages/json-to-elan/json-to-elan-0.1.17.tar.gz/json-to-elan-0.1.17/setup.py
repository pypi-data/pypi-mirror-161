# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_to_elan']

package_data = \
{'': ['*'],
 'json_to_elan': ['data/.gitkeep',
                  'data/.gitkeep',
                  'data/audio_1.json',
                  'data/audio_1.json']}

install_requires = \
['pympi-ling>=1.70.2,<2.0.0']

entry_points = \
{'console_scripts': ['make_elans = json_to_elan.make_elan:make_elan']}

setup_kwargs = {
    'name': 'json-to-elan',
    'version': '0.1.17',
    'description': 'The script reads a JSON file (or folder) and generates an ELAN file to match.',
    'long_description': '# JSON to ELAN\n\nThe script looks in a folder, and generates an ELAN file to match each JSON file.\n\n## JSON format\n\nIt has been written for the JSON output from Huggingface ASR pipelines. Here\'s an example of the expected JSON format. \n\n```json\n[\n    {\n        "text": "luanghan",\n        "timestamp":\n        [\n            1.16,\n            1.48\n        ]\n    },\n    {\n        "text": "ian",\n        "timestamp":\n        [\n            1.56,\n            1.7\n        ]\n    }\n]\n```\n\n## Basic usage\n\n\nPut your JSON files somewhere easily accessible, eg in a `data` folder in your working directory. Install it. Use it by providing a path to your data.\n\n```python\npip install json-to-elan\n```\n```python\nfrom json_to_elan import make_elan \nmake_elan(data_dir="content")\n```\n\n## Using this in Colab? \n\nTo use this in Google Colab, upload your JSON files into the File browser. Then define the data directory as:\n```python\ndata_dir="/content"\n``` \n\n\n## Options\n\nYou can also set a different tier name from the default (which is "default"). \n\nThe ELAN file gets a linked media file written, for which we assume that the media file is  a WAV with the same name as the JSON file. If you want to change this to MP3, change the audio_format. \n\nHere\'s an example:\n```python\nmake_elan(data_dir="content", tier_name="Words", audio_format="mp3")\n```\n\n',
    'author': 'Ben Foley',
    'author_email': 'ben@cbmm.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CoEDL/json-to-elan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
