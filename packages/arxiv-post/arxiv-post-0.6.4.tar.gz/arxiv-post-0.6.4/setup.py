# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arxiv_post', 'arxiv_post.apps']

package_data = \
{'': ['*']}

install_requires = \
['arxiv>=1.4,<2.0',
 'dateparser>=1.1,<2.0',
 'deepl>=1.4,<2.0',
 'fire>=0.4,<0.5',
 'more-itertools>=8.13,<9.0',
 'playwright>=1.18,<2.0',
 'pylatexenc>=2.10,<3.0',
 'requests>=2.27,<3.0',
 'tomli>=2.0,<3.0']

entry_points = \
{'console_scripts': ['arxiv-post = arxiv_post.cli:main']}

setup_kwargs = {
    'name': 'arxiv-post',
    'version': '0.6.4',
    'description': 'Translate and post arXiv articles to Slack and various apps',
    'long_description': '# arxiv-post\n\n[![Release](https://img.shields.io/pypi/v/arxiv-post?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/arxiv-post/)\n[![Python](https://img.shields.io/pypi/pyversions/arxiv-post?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/arxiv-post/)\n[![Downloads](https://img.shields.io/pypi/dm/arxiv-post?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/arxiv-post)\n[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.6127352-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.6127352)\n[![Tests](https://img.shields.io/github/workflow/status/astropenguin/arxiv-post/Tests?label=Tests&style=flat-square)](https://github.com/astropenguin/arxiv-post/actions)\n\nTranslate and post arXiv articles to Slack and various apps\n\n## Installation\n\n```shell\n$ pip install arxiv-post\n$ playwright install chromium\n```\n\n## Usage\n\nCommand line interface `arxiv-post` is available after installation, with which you can translate and post arXiv articles to various apps.\nNote that only `slack` app is currently available.\nYou need to [create a custom Slack app to get an URL of incoming webhook](https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack).\n\n```shell\n$ arxiv-post slack --keywords deshima \\\n                   --categories astro-ph.IM \\\n                   --target_lang ja \\\n                   --slack_webhook_url <Slack webhook URL>\n```\n\nThe posted article looks like this.\n\n![arxiv-post-slack.png](https://raw.githubusercontent.com/astropenguin/arxiv-post/master/docs/_static/arxiv-post-slack.png)\n\nFor detailed information, see the built-in help by the following command.\n\n```shell\n$ arxiv-post slack --help\n```\n\n## Example\n\nIt would be nice to regularly run the command by some automation tools such as GitHub Actions.\nHere is a live example where daily arXiv articles in [astro-ph.GA](https://arxiv.org/list/astro-ph.GA/new), [astro-ph.IM](https://arxiv.org/list/astro-ph.IM/new), and [astro-ph.HE](https://arxiv.org/list/astro-ph.HE/new) are posted to different channels of a Slack workspace.\n\n- [a-lab-nagoya/astro-ph-slack: Translate and post arXiv articles to Slack](https://github.com/a-lab-nagoya/astro-ph-slack)\n\n## References\n\n- [fkubota/Carrier-Owl: arxiv--> DeepL --> Slack](https://github.com/fkubota/Carrier-Owl): The arxiv-post package is highly inspired by their work.\n',
    'author': 'Akio Taniguchi',
    'author_email': 'taniguchi@a.phys.nagoya-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/astropenguin/arxiv-post/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
