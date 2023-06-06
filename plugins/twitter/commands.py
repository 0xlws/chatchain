import os
from plugins.twitter.twitter import custom_tweet, tweet_img


def setup(self):
    # twitter
    @self.assistant.command()
    async def tweet(ctx, *, tweet_content):
        custom_tweet(tweet_content)
        await ctx.send("Your tweet has been sent.")

    @self.assistant.command()
    async def tweet_image(ctx, image_path, image_filename, *, tweet_content):
        tweet_img(image_path, image_filename, tweet_content)
        await ctx.send("Your tweet has been sent.")
