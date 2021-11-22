from pathlib import Path
from time import sleep
from typing import List, Tuple, Union
from urllib.request import Request, urlopen

import pandas as pd
import tweepy
import yaml
from tqdm import tqdm

from utils.image import download_from_hashtag
from utils.tweet import save_user_tweet


def download():
    with open("./config.yaml") as f:
        config = yaml.safe_load(f)
    auth = tweepy.OAuthHandler(config["API_KEY"], config["API_KEY_SECRET"])
    auth.set_access_token(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth)

    print("##### download hashtag tweet #####")
    df = pd.read_csv(config["hashtag_list_data"], dtype=str)
    download_from_hashtag(df, api, config)

    print("##### download user tweet #####")
    df = pd.read_csv(config["user_list_data"], dtype=str)
    save_user_tweet(df, api, config)

    print("Done")


if __name__ == "__main__":
    download()
