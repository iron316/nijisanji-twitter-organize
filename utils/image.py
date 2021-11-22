from pathlib import Path
from time import sleep
from typing import Dict, List, Tuple, Union
from urllib.request import Request, urlopen

import pandas as pd
import tweepy
import yaml
from tqdm import tqdm

THRESHOLD = 50


def check_tweet(
    results: List[tweepy.models.Status], logs: List[str]
) -> List[tweepy.models.Status]:
    checked_tweet: List[tweepy.models.Status] = []
    for res in results:
        if (
            res.id not in logs
            and res.favorite_count >= THRESHOLD  # いいねが閾値以下のものを取得
            and hasattr(res, "extended_entities")  # 画像が付いていないものは除外
        ):
            checked_tweet.append(res)
    return checked_tweet


def get_hashtag_tweet_list(
    hashtag: str, logs: List[str], api: tweepy.API
) -> Tuple[List[tweepy.models.Status], str]:
    tweets: List[tweepy.models.Status] = []
    max_id = None
    while True:
        if max_id is None:
            results = api.search_tweets(
                q=hashtag + f" -filter:retweets min_faves:{THRESHOLD}",
                result_type="recent",
            )
        else:
            results = api.search_tweets(
                q=hashtag + f" -filter:retweets min_faves:{THRESHOLD}",
                max_id=max_id,
                result_type="recent",
            )
        if len(results) == 0:
            break
        else:
            tweets += check_tweet(results, logs)
            max_id = str(int(results[-1].id) - 1)
        sleep(1.0)
        print(".", end="", flush=True)
    return tweets


def download_image(tweet: tweepy.models.Status, save_path: Path):
    media = tweet.extended_entities["media"]
    for i, m in enumerate(media):
        url = m["media_url_https"]
        dst_path = save_path / f"{tweet.user.screen_name}_{tweet.id}_{i}.jpeg"
        try:
            req = Request(url)
            with urlopen(req) as response:
                with dst_path.open("wb") as f:
                    f.write(response.read())
        except:
            pass


def download_from_hashtag(
    df: pd.DataFrame, api: tweepy.API, config: Dict[str, str]
) -> None:
    log_path = Path(config["save_dir"]) / "logs"
    log_path.mkdir(exist_ok=True, parent=True)
    for i, row in df.iterrows():
        print(f"START {row['hashtag']}")
        save_path = Path(config["save_dir"]) / row["name"]
        save_path.mkdir(exist_ok=True, parents=True)
        log_file = log_path / f"{row['name']}_log.txt"
        if log_file.exists():
            with log_file.open("r") as f:
                logs = f.readlines()
        else:
            with log_file.open("w") as f:
                log_file.write("")
            logs = []
        tweets = get_hashtag_tweet_list(row["hashtag"], logs, api)
        print(f"Found {len(tweets)} tweet")
        with log_file.open("a") as f:
            for tweet in tqdm(tweets):
                download_image(tweet, save_path)
                sleep(0.3)
            log_file.write(tweet.id)
        df.to_csv(config["hashtag_list_data"], index=False)
