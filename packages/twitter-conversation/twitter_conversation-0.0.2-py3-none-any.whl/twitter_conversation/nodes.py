import tweepy
from neomodel import StructuredNode, IntegerProperty, StructuredRel, RelationshipFrom


class Tweet(StructuredNode):
    """
    This class describes a basic tweet in its function as a node within a conversation.

    This class can be used to formally build a conversation graph.
    All other information regarding the tweets can be added in more specific classes afterwards.
    """
    # Properties
    twitter_id: int = IntegerProperty(required=True, unique_index=True)
    conversation_id: int = IntegerProperty(required=True, index=True)
    # Relationships
    reply: StructuredRel = RelationshipFrom('Tweet', 'reply')

    @staticmethod
    def convert(tweet: tweepy.Tweet):
        """
        This method maps the basic structure of a tweepy.Tweet to this Tweet.
        :param tweet: A tweepy.Tweet.
        :return: The mapping of variables.
        """
        return {
            'twitter_id': tweet.data.get('id', None),
            'conversation_id': tweet.data.get('conversation_id', None)
        }
