import tweepy
from plugins.config.config_env import (
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    API_KEY,
    API_SECRET_KEY,
    BEARER_TOKEN,
)

auth = tweepy.OAuth1UserHandler(
    API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)


def custom_tweet(tweet):
    client.create_tweet(text=tweet)


def tweet_img(image_path, image_filename, tweet):
    with open(image_path, "rb") as image_file:
        media_id = api.media_upload(image_filename, file=image_file).media_id_string

    client.create_tweet(text=tweet, media_ids=[media_id])
