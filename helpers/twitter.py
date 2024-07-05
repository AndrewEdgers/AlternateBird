import os
from datetime import datetime
import logging

import discord
import requests
from dotenv import load_dotenv
import pytz

from helpers import methods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_bot")

config = methods.load_config()
load_dotenv()

# Discord webhook URL from environment variable
DISCORD_WEBHOOK_URL = os.getenv("TWITTER_WEBHOOK")

# The profile image URL of alt_esports_ for the webhook avatar
ALT_ESPORTS_PROFILE_IMAGE_URL = "https://pbs.twimg.com/profile_images/1799238298961145856/hhni-k3x_normal.jpg"


# Function to get the token based on the Tweet ID
def get_token(tweet_id):
    return ((int(tweet_id) / 1e15) * 3.141592653589793).hex()[2:].replace("0", "").replace(".", "")


# Function to fetch tweet data from Twitter's embedding API
async def fetch_tweet(tweet_id):
    token = get_token(tweet_id)
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token={token}&lang=en"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching tweet {tweet_id}: {e}")
    except ValueError as e:
        logger.error(f"Error parsing JSON response for tweet {tweet_id}: {e}")
    return None


# Function to get high-resolution profile image URL
def get_high_res_profile_image_url(url):
    return url.replace("_normal", "_400x400")


# Function to send a message to Discord
async def send_to_discord(content, tweet_text, media_url, author_name, author_url, author_icon_url, created_at):
    if DISCORD_WEBHOOK_URL:
        embed = {
            "author": {
                "name": f"{author_name} (@{author_name})",
                "url": author_url,
                "icon_url": author_icon_url
            },
            "description": tweet_text,
            "color": discord.Color.from_str(config["main_color"]).value,
            "footer": {
                "text": f"{created_at.strftime('%Y-%m-%d %H:%M:%S CST')}"
            }
        }

        if media_url:
            embed["image"] = {"url": media_url}

        data = {
            "content": content,
            "embeds": [embed],
            "avatar_url": get_high_res_profile_image_url(ALT_ESPORTS_PROFILE_IMAGE_URL)
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            logger.info('Message sent successfully')
        else:
            logger.error(f'Failed to send message: {response.status_code}, {response.text}')
    else:
        logger.error("Discord webhook URL is not set.")


# Main function to fetch a tweet and post it to Discord
async def twitter(tweet_id, message):
    tweet_data = await fetch_tweet(tweet_id)
    if tweet_data:
        tweet_text = tweet_data.get('text')
        profile_image_url = tweet_data['user']['profile_image_url_https']
        username = tweet_data['user']['screen_name']
        author_name = tweet_data['user']['name']
        author_url = f"https://twitter.com/{username}"
        created_at_utc = datetime.strptime(tweet_data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        central = pytz.timezone('US/Central')
        created_at_central = created_at_utc.astimezone(central)

        if username != "alt_esports_":
            content = (f"[Retweeted](https://twitter.com/alt_esports_/status/{tweet_id})"
                       f" [@{username}](https://twitter.com/{username})")
            author_icon_url = get_high_res_profile_image_url(profile_image_url)
        else:
            content = f"[Tweeted](https://twitter.com/{username}/status/{tweet_id})"
            author_icon_url = ""

        # Check for media in the tweet
        media_url = None
        if 'mediaDetails' in tweet_data and tweet_data['mediaDetails']:
            media_details = tweet_data['mediaDetails'][0]
            if 'media_url_https' in media_details:
                media_url = media_details['media_url_https']
            elif 'video_info' in media_details and 'variants' in media_details['video_info']:
                media_url = media_details['video_info']['variants'][0]['url']

        if message:
            content = message + f"\n{content}"
        await send_to_discord(content, tweet_text, media_url, author_name, author_url, author_icon_url, created_at_central)
    else:
        logger.error("Failed to fetch tweet data.")


# Example usage
if __name__ == "__main__":
    # Replace with the actual Tweet ID you want to fetch and post
    tweet_id = "1805251519077638318"  # Example Tweet ID
    twitter(tweet_id, None)
