# Obtaining Twitter Conversations

It is often necessary to pull not only individual tweets but entire conversations from Twitter.

With the new [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api), it is possible
that entire [conversations](https://help.twitter.com/en/using-twitter/twitter-conversations) can now
be queried via
the [conversation_id](https://developer.twitter.com/en/docs/twitter-api/conversation-id) field.

This project features the reconstruction of single or multiple conversations via already known
entries of `conversation_id` or the search for such conversation-starting tweets on a given topic
and related conversations within a given time period.

# Setup :building_construction:

For this project [Python 3.10](https://www.python.org/downloads/release/python-3100/) is
required and must be installed on the hosting device.

Furthermore, [Poetry](https://python-poetry.org) is used as package manager.
Any other python package manager works as well.

This project can be installed directly as a Python package using the following command:

```
    poetry add twitter-conversation
```

During the installation of the submodule [neomodels](https://neomodel.readthedocs.io/en/latest/)
an error may occur because [geos](https://trac.osgeo.org/geos) must be installed.

## Additional Stuff :nut_and_bolt:

1. [Docker](https://www.docker.com)
2. [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api) (Apply for access and use
   the [Bearer-Token](https://oauth.net/2/bearer-tokens/))

# About Conversations on Twitter :bulb:

To reconstruct or obtain conversations on Twitter, the reply-tree is used as a fundamental data
structure.
A reply-tree is a rooted in-tree which is characterized by a root-tweet and reply-tweets which can
reach this designated tweet.

A root-tweet is a conversation-starting tweet if it has at least one reply-tweet and thus creates a
conversation. A conversation is a reply-tree which does not only consists of a root-tweet.

This term reply-tree in a conversation on Twitter is also referred to as a conversation-thread.
Furthermore, Twitter assigns the field `conversation_id` to each tweet of a conversation.
The `conversation_id` is the ID of this tweet, which was the first tweet of the conversation and
thus started the conversation.

Therefore, as a starting point for reconstructing and obtaining conversations, the IDs of those
tweets that sparked a conversation are necessary.

# Getting things started :rocket:

The enclosed `/scripts/`-folder can be taken for example of how to apply this library.
It is important to note that some of them may need a running Neo4j instance to write the tweets and
reply-relationships.

All available scripts are mentioned in the `[tool.poetry.scripts]` of `pyproject.toml`.
To see how a specific script works use:

```
   poetry run <name-of-script> --help
```

To use the scripts with Docker run:

```
   docker-compose run twitter sh -c "./wait-for-it.sh neo_db:7687 -- poetry run <name-of-script> <mode> <flags>
```
