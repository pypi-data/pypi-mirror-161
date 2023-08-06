import argparse
import datetime
import os
from pathlib import Path
from typing import List

import pandas as pd
import tweepy as tweepy
from neomodel import config, install_all_labels

from twitter_conversation.obtain import ReplyTree


def main():
    parser = argparse.ArgumentParser(description="Just a python script of how to obtain Twitter conversations.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-s", "--start", type=datetime.datetime.fromisoformat,
                        default=datetime.datetime(tzinfo=datetime.timezone.utc,
                                                  year=2006, month=3, day=21,
                                                  hour=0, minute=0, second=0, microsecond=0),
                        # The first day of the Twitter-database records
                        help="The utc-time in the past where to start the search (default today \
                                                 0 o'clock).")

    parser.add_argument("-e", "--end", type=datetime.datetime.fromisoformat,
                        default=datetime.datetime.utcnow() - datetime.timedelta(seconds=10),
                        # This day but at now.
                        help="The utc-time where to end the search (default today).")

    subparsers = parser.add_subparsers(help='The mode for obtaining conversations.', required=True, dest="mode")

    # Conversation by one single conversation_id
    parser_conversation_id = subparsers.add_parser('single_conversation',
                                                   help='Use if a single conversation should be reconstructed \
                                                       while providing only one conversation_id.')

    parser_conversation_id.add_argument("-c", "--conversation", type=int,
                                        required=True,
                                        help="A single conversation_id of the conversation which should \
                                            be reconstructed")

    # Conversations by a csv-file having the IDs of conversation-starting Tweets.
    parser_conversation_starting_tweets = subparsers.add_parser('multiple_conversations',
                                                                help='Use if multiple conversations should be \
                                                                    reconstructed while providing a csv-file holding the \
                                                                    IDs of conversation-starting Tweets.')

    parser_conversation_starting_tweets.add_argument("-s", "--starting_tweets", type=Path,
                                                     required=True,
                                                     help="A path to a csv-file having all IDs of conversation-starting\
                                                         Tweets in a column twitter_id.")

    # Search for conversation starting Tweets
    parser_search_conversations = subparsers.add_parser('search_conversations',
                                                        help='Use if conversations should be obtained by searching\
                                                            for root-tweets by their topic.')

    parser_search_conversations.add_argument("-t", "--topic", type=str, default='abortion',
                                             help="The topic-word (hashtag eg. #<abortion>) of which to be present\
                                                 in the root-tweets.")

    args = parser.parse_args()
    args_config = vars(args)

    print('########## CONFIGURATION ##########')
    for argument, value in args_config.items():
        print(argument, ':', value)

    print('########## SETUP ##########')
    # setup tweepy-client
    client = tweepy.Client(
        bearer_token=os.environ['BEARER_TOKEN'],
        wait_on_rate_limit=True
    )

    # setup db-client
    authentication: List[str] = os.environ.get('NEO4J_AUTH').split('/')
    db_user: str = authentication[0]
    db_password: str = authentication[1]
    db_host: str = os.environ.get('DB_HOST')

    config.DATABASE_URL = 'bolt://{user}:{password}@{host}:7687'.format(user=db_user,
                                                                        password=db_password,
                                                                        host=db_host)
    install_all_labels()

    print('########## OBTAIN ##########')
    # Decide how to obtain conversations
    if args_config.get('mode') == "single_conversation":
        ReplyTree(client,
                  conversation_id=args_config.get('conversation'),
                  start_time=args_config.get('start'),
                  max_results=500) \
            .obtain()
    elif args_config.get('mode') == "multiple_conversations":
        conversation_starting_tweets: pd.DataFrame = pd.read_csv(args_config.get('starting_tweets'),
                                                                 index_col='twitter_id')
        for conversation_starting_tweet in conversation_starting_tweets.index:
            ReplyTree(client,
                      conversation_id=conversation_starting_tweet,
                      start_time=args_config.get('start'),
                      max_results=500) \
                .obtain()
    elif args_config.get('mode') == "search_conversations":
        for page in tweepy.Paginator(
                client.search_all_tweets,
                query=f"(#{args_config.get('topic')}) lang:en -is:reply -is:retweet -is:quote",
                tweet_fields=['conversation_id'],
                max_results=500,
                start_time=args_config.get('start'),
                end_time=args_config.get('end'),
                sort_order='relevancy'
        ):
            for tweet in page.data:
                ReplyTree(client,
                          conversation_id=tweet.conversation_id,
                          start_time=args_config.get('start'),
                          max_results=500) \
                    .obtain()
    print('########## CONGRATULATION ##########')


if __name__ == '__main__':
    main()
