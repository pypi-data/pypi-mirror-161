import datetime
import time
from typing import List

import tweepy
from tweepy import ReferencedTweet, Tweet
from twitter_conversation.nodes import Tweet as NeoTweet


class ReplyTree:
    """
    This class is to write structural Reply-Trees, as they are specified by nodes having only the id of the associated
    Tweet and the corresponding conversation_id as well as the reply-Relation as edges, to a running Neo4j instance.
    """

    def __init__(self, client: tweepy.Client, conversation_id: int, **kwargs) -> None:
        """
        This method initializes the ReplyTree class.
        It is important to provide the initialized client of tweepy for calling the Twitter-API v2.
        Furthermore, the conversation_id is to be given to this class for reconstructing the associated Reply-Tree.
        To specify the search option of tweepy.search_all_tweets, which is used for obtaining Reply-Trees, kwargs can
        be used.
        :param client: The initialized tweepy client to call Twitter-API v2.
        :param conversation_id: The conversation who's Reply-Tree should be reconstructed.
        :param kwargs: Additional search options for client.search_all_tweets.
        """
        self.client = client
        self.conversation_id = conversation_id
        self.kwargs = kwargs

    def obtain(self) -> None:
        """
        This method can be used to obtain the Reply-Trees by the used conversation_id and all additional attributes.

        The conversation can be obtained since Twitter associates a Reply-Tree to each particular conversation_id and
        writes the structural Reply-Tree to the specified Neo4j-Database.

        Therefore, if the conversation-starting Tweet is known the conversation can be reconstructed.

        Furthermore, it should be noticed that this method only obtains Reply-Trees.
        This is a simplification for conversations since Retweets would always refer to the original Tweet where
        all Replys to the Retweet would also be added to the conversation of the original Tweet.
        Quotes (Retweet + text), on the other side, would create a different context if a Tweet of the conversation is
        cited to be forwarded. This would create a new side-conversation with another conversation_id. Otherwise, if a
        Tweet of the same conversation is quoted as a Reply the conversation_id stays the same. The same holds if the
        Reply quotes a Tweet of another conversation. In this case the quoted Tweet is added as a URL to the quoting
        Reply.

        :return: Nothing.
        """
        t0_global: float = time.time()
        print("Obtain Reply-Tree: ", self.conversation_id)

        for page in tweepy.Paginator(
                self.client.search_all_tweets,
                # conversation with error (1469222907477962753), conversation with quote (1455259652300566530)
                # Quote of Tweet in 1455259652300566530 with own conversation (1550189058059653122)
                query=f'conversation_id:{self.conversation_id}',
                # these fields are mandatory because they minimally describe a Reply-Tree.
                tweet_fields=['conversation_id', 'referenced_tweets'],
                **self.kwargs
        ):
            # Each page is the Response(data, includes, errors, meta) of size max_results.
            # Data will contain the requested Tweets holding the information defined in tweet_fields.
            # Includes provide all further information for the Tweets in Data which was specified in expansions.
            # Error will show all minimal information to reconstruct Tweets leading to error because of deletion etc...
            t0: float = time.time()
            if not page.data:
                # in the case there is no conversation present because there is only a Root-Tweet.
                time.sleep(1 - (time.time() - t0) % 1)
                continue
            for tweet in page.data:
                # <Response>.data contains all resulting Tweets having the requested information in data.
                # The nodes in <Response>.data are accessible and can therefore be directly written into the database.
                neo_tweet: NeoTweet = NeoTweet.get_or_create(NeoTweet.convert(tweet))[0]

                # If a Tweet holds the field referenced_tweets then there exists at least one other Tweet referenced.
                if tweet.referenced_tweets:
                    # The referenced Tweets can be accessed and provide the type
                    # (Reply, Retweet, Quote (Retweet + text)).
                    # A Quote can also be a Reply in a conversation but with a Link to the original Tweet.
                    # Furthermore, if Quote is used as a Reply by quoting a Tweet of another conversation the
                    # conversation_id of the referenced_tweet is taken and not the one of the quoted (original) Tweet.
                    # A Reply binds a Tweet to a conversation (Reply-tree)
                    references: List[ReferencedTweet] = tweet.referenced_tweets
                    # The conversation (reply-tree) is reconstructed by using the conversation_id.
                    # Therefor, if a Tweets has a non-empty reference_tweets-field, it can be assumed to have at least
                    # one Reply-Tweet.
                    referenced_tweet: ReferencedTweet = next(filter(lambda ref: ref.type == "replied_to", references))
                    # If a Tweet references to another Tweet via the replied_to-relation the referencing Tweets is a
                    # Reply to the referenced Tweet in the same conversation (Reply-tree).
                    neo_referenced_tweet: NeoTweet = NeoTweet.get_or_create(
                        NeoTweet(twitter_id=referenced_tweet.id, conversation_id=neo_tweet.conversation_id).__dict__
                    )[0]
                    neo_referenced_tweet.reply.connect(neo_tweet)

            time.sleep(1 - (time.time() - t0) % 1)
        print("Took:", str(datetime.timedelta(seconds=time.time() - t0_global)))
        print("Obtained Tweets:", len(NeoTweet.nodes.filter(conversation_id=self.conversation_id).all()))
