# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['translator_template', 'translator_template.tests']

package_data = \
{'': ['*'],
 'translator_template': ['data/*'],
 'translator_template.tests': ['data/*']}

entry_points = \
{'console_scripts': ['generate = translator_template.app:main']}

setup_kwargs = {
    'name': 'translator-template',
    'version': '0.2.4',
    'description': 'Utility for generating a Microsoft Word file from a simple document description, for translators.',
    'long_description': '# translator-template\nGenerate a Word Document Template for Translator\n\n## Prerequisite\n\n* python 3.7 or greater\n* poetry\n\nDownload the dependent modules by running `poetry install`\n\n## Running the code\n\n```\npoetry run generate --in-file {input-text-file} --out-file {output-docx-file}\n```\n\nIf the `--out-file` argument is omitted, the `--in-file` argument value is used, with the extension replaced with `.docx`.\n\n## Input Format Specification\n\nIn regular expression form the input is the following:\n\n`^((\\d|\\*\\d+\\*)-?)*$`\n\nFor a given page, the number of panels is represented either by a single digit if the count of panels is fewer than 10.  When the count of panels is greater than or equal to 9, the count is sandwiched between a pair of asterisks.\n\nThe panel count can be optionally followed by a hyphen.  This signifies that the panels span two pages.\n\n## Output Specification\n\nThe output is a Word DOCX file.  This contains three paragraph styles:\n\n* PagePara\n* PanelPara\n* QuotePara\n',
    'author': 'Chris Thrasher',
    'author_email': 'cthrash@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
