# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['commonregex']
install_requires = \
['regex>=2022.4.24,<2023.0.0']

setup_kwargs = {
    'name': 'commonregex-improved',
    'version': '1.0.0',
    'description': 'An improved version of original commonregex. Find all dates, times, emails, phone numbers, links, emails, ip addresses, prices, bitcoin address, and more in a string.',
    'long_description': '<br><br>\n\n<h1 align="center">CommonRegex Improved</h1>\n\n<p align="center">\n  <a href="/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg"/></a>\n  <!-- <img alt="PyPI - Downloads" src="https://pepy.tech/badge/commonregex-improved/month"> -->\n   <img alt="PyPI - Downloads" src="https://pepy.tech/badge/commonregex-improved">\n   <a href="https://twitter.com/brootware"><img src="https://img.shields.io/twitter/follow/brootware?style=social" alt="Twitter Follow"></a>\n   <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/commonregex-improved"> <img alt="PyPI" src="https://img.shields.io/pypi/v/commonregex-improved">\n   <a href="https://sonarcloud.io/summary/new_code?id=brootware_commonregex-improved"><img src="https://sonarcloud.io/api/project_badges/measure?project=brootware_commonregex-improved&metric=alert_status" alt="reliability rating"></a>\n   <img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/brootware/commonregex-improved/CI?label=CI&branch=main">\n</p>\n\n<p align="center">\n  An improved version of commonly used regular expressions in Python\n</p>\n\n<br><br>\n\n> Inspired by and improved upon [CommonRegex](https://github.com/madisonmay/CommonRegex)\n\nThis is a collection of commonly used regular expressions. This library provides a simple API interface to match the strings corresponding to specified patterns.\n\n## Installation\n\n```pip install --upgrade commonregex-improved```\n\n## Usage\n\n```python\nimport commonregex as CommonRegex\n\ntext = "John, please get that article on www.linkedin.com to me by 5:00PM on Jan 9th 2012. 4:00 would be ideal, actually or 5:30 P.M. If you have any questions, You can reach me at (519)-236-2723x341 or get in touch with my associate at harold_smith@gmail.com. You can find my ip address at 127.0.0.1 or at 64.248.67.225. I also have a secret protected with md5 8a2292371ee60f8212096c06fe3335fd. The internal webpage to get the article from is https://internal.sharepoint.edu.au"\n\ndate_list = CommonRegex.dates(text)\n# [\'Jan 9th 2012\']\ntime_list = CommonRegex.times(text)\n# [\'5:00PM\', \'4:00 \', \'5:30 P.M.\']\nurl_list = CommonRegex.links(text)\n# [\'www.linkedin.com\', \'gmail.com\', \'https://internal.sharepoint.edu.au\']\nphone_list = CommonRegex.phones_with_exts(text)  \n# [\'(519)-236-2723x341\']\nip_list = CommonRegex.ips(text)\n# [\'127.0.0.1\', \'64.248.67.225\']\nemail_list = CommonRegex.emails(text)\n# [\'harold_smith@gmail.com\']\nmd5_list = CommonRegex.md5_hashes(text)\n# [\'8a2292371ee60f8212096c06fe3335fd\']\n```\n\n## ⚔️ Performance benchmark\n\n[CommonRegex](https://github.com/madisonmay/CommonRegex) is awesome!\n\nSo why re-implement the popular original commonregex project? The API calls to each of the regular expressions are really slow.\n\nIt takes 12 seconds for a total of 2999 calls to Dates function in the original version of CommonRegex. While the improved version of CommonRegex with the same number of calls merely takes 2 seconds.\n\n![improved](./benchmark/benchmark.png)\n\nYou can find more detailed results about [original](./benchmark/original_cregex_result.pdf) and [improved](./benchmark/cregex_improved_result.pdf) versions.\n\n## Features / Supported Methods\n\n* `dates(text: str)`\n* `times(text: str)`\n* `phones(text: str)`\n* `phones_with_exts(text: str)`\n* `links(text: str)`\n* `emails(text: str)`\n* `ipv4s(text: str)`\n* `ipv6s(text: str)`\n* `ips(text: str)`\n* `not_known_ports(text: str)`\n* `prices(text: str)`\n* `hex_colors(text: str)`\n* `credit_cards(text: str)`\n* `visa_cards(text: str)`\n* `master_cards(text: str)`\n* `btc_address(text: str)`\n* `street_addresses(text: str)`\n* `zip_codes(text: str)`\n* `po_boxes(text: str)`\n* `ssn_numbers(text: str)`\n* `md5_hashes(text: str)`\n* `sha1_hashes(text: str)`\n* `sha256_hashes(text: str)`\n* `isbn13s(text: str)`\n* `isbn10s(text: str)`\n* `mac_addresses(text: str)`\n* `iban_numbers(text: str)`\n* `git_repos(text: str)`\n',
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
