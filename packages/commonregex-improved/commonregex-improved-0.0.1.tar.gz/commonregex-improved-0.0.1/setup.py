# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['commonregex_improved']
install_requires = \
['regex>=2022.4.24,<2023.0.0']

setup_kwargs = {
    'name': 'commonregex-improved',
    'version': '0.0.1',
    'description': 'Python cli tool to redact sensitive data',
    'long_description': '<br><br>\n\n<h1 align="center">CommonRegex Improved</h1>\n\n<p align="center">\n  <a href="/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg"/></a>\n  <img alt="PyPI - Downloads" src="https://pepy.tech/badge/pyredactkit/month">\n   <!-- <img alt="PyPI - Downloads" src="https://pepy.tech/badge/pyredactkit"> -->\n   <a href="https://twitter.com/brootware"><img src="https://img.shields.io/twitter/follow/brootware?style=social" alt="Twitter Follow"></a>\n   <!-- <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/commonregex-improved"> <img alt="PyPI" src="https://img.shields.io/pypi/v/commonregex-improved"> -->\n   <!-- <a href="https://sonarcloud.io/summary/new_code?id=brootware_PyRedactKit"><img src="https://sonarcloud.io/api/project_badges/measure?project=brootware_PyRedactKit&metric=alert_status" alt="reliability rating"></a> -->\n   <img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/brootware/pyredactkit/CI?label=CI&branch=dev">\n</p>\n\n<p align="center">\n  An improved version of commonly used regular expressions in Python\n</p>\n\n<br><br>\n\n> Inspired by and improved upon [CommonRegex](https://github.com/madisonmay/CommonRegex)\n\nThis is a collection of commonly used regular expressions. This library provides a simple API interface to match the strings corresponding to specified patterns.\n\n## Installation\n\n```pip install --upgrade commonregex-improved```\n\n## Usage\n\n```python\nimport commonregex-improved as CommonRegex\n\ntext = "John, please get that article on www.linkedin.com to me by 5:00PM on Jan 9th 2012. 4:00 would be ideal, actually. If you have any questions, You can reach me at (519)-236-2723x341 or get in touch with my associate at harold.smith@gmail.com"\n\ndate_list = CommonRegex.dates(text)\n# [\'Jan 9th 2012\']\ntime_list = CommonRegex.times(text)\n# [\'5:00PM\', \'4:00\']\nurl_list = CommonRegex.links(text)\n# [\'www.linkedin.com\', \'harold.smith@gmail.com\']\nphone_list = CommonRegex.phones_with_exts(text)  \n# [\'(519)-236-2723x341\']\nemail_list = CommonRegex.emails(text)\n# [\'harold.smith@gmail.com\']\nidentify_all = CommonRegex.find_all(text)\n# Do note that the regexes might clash for this find_all function\n# [\'Jan 9th 2012\', \'5:00\', \'(519)-236-2723\', \'(519)-236-2723x341\', \'harold.smith@gmail.com\', \'www.linkedin.com\']\n```\n\n## ⚔️ Performance benchmark\n\n[CommonRegex](https://github.com/madisonmay/CommonRegex) is awesome!\n\nSo why re-implement the popular original commonregex project? The API calls to each of the regular expressions are really slow. It takes 12 seconds for a total of 2999 calls to Dates function in the original version of CommonRegex.\n\n![original](./benchmark/original.png)\n\nHere is the improved version of CommonRegex with the same number of calls. It merely takes 2 seconds.\n\n![improved](./benchmark/improved.png)\n\nYou can find more detailed results about [original](./benchmark/original_cregex_result.pdf) and [improved](./benchmark/cregex_improved_result.pdf) versions.\n\n## Supported methods\n',
    'author': 'brootware',
    'author_email': 'brootware@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brootware/commonregex-improved',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
