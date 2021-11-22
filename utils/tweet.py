from pathlib import Path
from time import sleep
from typing import Dict, List, Tuple, Union
from urllib.request import Request, urlopen

import pandas as pd
import tweepy
import yaml
from tqdm import tqdm

from .image import download_image


def check_user_tweet(results: List[tweepy.models.Status]) -> List[tweepy.models.Status]:
    checked_tweet: List[tweepy.models.Status] = []
    for res in results:
        if not res.text.startswith("RT @"):
            checked_tweet.append(res)
    return checked_tweet


def get_user_tweet_list(
    user_id: str, since_id: str, api: tweepy.API
) -> Tuple[List[tweepy.models.Status], str]:
    tweets: List[tweepy.models.Status] = []
    max_id = None
    while True:
        if max_id is None:
            results = api.user_timeline(
                screen_name=user_id, since_id=since_id, count=200
            )
        else:
            results = api.user_timeline(
                screen_name=user_id, since_id=since_id, max_id=max_id, count=200
            )
        if len(results) == 0:
            break
        else:
            tweets += check_user_tweet(results)
            max_id = str(int(results[-1].id) - 1)
        sleep(1.0)
        print(".", end="", flush=True)
    return tweets


def save_user_tweet(df: pd.DataFrame, api: tweepy.API, config: Dict[str, str]) -> None:
    save_dir = Path(config["save_dir"]) / "user_tweet"
    for i, row in df.iterrows():
        print(f"START {row['user_id']}-{row['name']}")
        user_dir = save_dir / row["name"]
        image_path = user_dir / "image"
        image_path.mkdir(exist_ok=True, parents=True)
        csv_path = user_dir / "tweet.csv"

        tweets = get_user_tweet_list(row["user_id"], row["since_id"], api)
        if csv_path.exists():
            user_df = pd.read_csv(csv_path, dtype=str)
        else:
            user_df = pd.DataFrame(
                [], columns=["id", "text", "create_at", "media_url", "name"]
            )
        print(f"Found {len(tweets)} tweet")
        for tweet in tqdm(tweets[::-1]):
            row = {
                "id": tweet.id,
                "text": tweet.text,
                "create_at": tweet.created_at,
                "media_url": None,
                "name": tweet.user.name,
            }
            if hasattr(tweet, "extended_entities"):
                url = ""
                for m in tweet.extended_entities["media"]:
                    url += m["media_url_https"] + " "
                row["media_url"] = url.strip()
                download_image(tweet, image_path)

            user_df = user_df.append(row, ignore_index=True)
        if len(tweets) != 0:
            df["since_id"].iloc[i] = tweets[0].id
        df.to_csv(config["user_list_data"], index=False)

        user_df.to_csv(csv_path, index=False)
