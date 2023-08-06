# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['twitter_conversation', 'twitter_conversation.scripts']

package_data = \
{'': ['*']}

install_requires = \
['neomodel>=4.0.8,<5.0.0', 'pandas>=1.4.3,<2.0.0', 'tweepy>=4.10.0,<5.0.0']

entry_points = \
{'console_scripts': ['obtain_reply_tree = '
                     'twitter_conversation.scripts.reply_tree:main']}

setup_kwargs = {
    'name': 'twitter-conversation',
    'version': '0.0.2',
    'description': 'This is a project to obtain Twitter conversation over the Twitter-API v2 and to store them with Neo4j.',
    'long_description': '# Obtaining Twitter Conversations\n\nIt is often necessary to pull not only individual tweets but entire conversations from Twitter.\n\nWith the new [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api), it is possible\nthat entire [conversations](https://help.twitter.com/en/using-twitter/twitter-conversations) can now\nbe queried via\nthe [conversation_id](https://developer.twitter.com/en/docs/twitter-api/conversation-id) field.\n\nThis project features the reconstruction of single or multiple conversations via already known\nentries of `conversation_id` or the search for such conversation-starting tweets on a given topic\nand related conversations within a given time period.\n\n# Setup :building_construction:\n\nFor this project [Python 3.10](https://www.python.org/downloads/release/python-3100/) is\nrequired and must be installed on the hosting device.\n\nFurthermore, [Poetry](https://python-poetry.org) is used as package manager.\nAny other python package manager works as well.\n\nThis project can be installed directly as a Python package using the following command:\n\n```\n    poetry add twitter-conversation\n```\n\nDuring the installation of the submodule [neomodels](https://neomodel.readthedocs.io/en/latest/)\nan error may occur because [geos](https://trac.osgeo.org/geos) must be installed.\n\n## Additional Stuff :nut_and_bolt:\n\n1. [Docker](https://www.docker.com)\n2. [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api) (Apply for access and use\n   the [Bearer-Token](https://oauth.net/2/bearer-tokens/))\n\n# About Conversations on Twitter :bulb:\n\nTo reconstruct or obtain conversations on Twitter, the reply-tree is used as a fundamental data\nstructure.\nA reply-tree is a rooted in-tree which is characterized by a root-tweet and reply-tweets which can\nreach this designated tweet.\n\nA root-tweet is a conversation-starting tweet if it has at least one reply-tweet and thus creates a\nconversation. A conversation is a reply-tree which does not only consists of a root-tweet.\n\nThis term reply-tree in a conversation on Twitter is also referred to as a conversation-thread.\nFurthermore, Twitter assigns the field `conversation_id` to each tweet of a conversation.\nThe `conversation_id` is the ID of this tweet, which was the first tweet of the conversation and\nthus started the conversation.\n\nTherefore, as a starting point for reconstructing and obtaining conversations, the IDs of those\ntweets that sparked a conversation are necessary.\n\n# Getting things started :rocket:\n\nThe enclosed `/scripts/`-folder can be taken for example of how to apply this library.\nIt is important to note that some of them may need a running Neo4j instance to write the tweets and\nreply-relationships.\n\nAll available scripts are mentioned in the `[tool.poetry.scripts]` of `pyproject.toml`.\nTo see how a specific script works use:\n\n```\n   poetry run <name-of-script> --help\n```\n\nTo use the scripts with Docker run:\n\n```\n   docker-compose run twitter sh -c "./wait-for-it.sh neo_db:7687 -- poetry run <name-of-script> <mode> <flags>\n```\n',
    'author': 'Marc Feger',
    'author_email': 'marc.feger@uni-duesseldorf.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.cs.uni-duesseldorf.de/feger/twitter-conversation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
