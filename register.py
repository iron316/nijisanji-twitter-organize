from pathlib import Path

import pandas as pd
import tweepy
import yaml


def registration_user(query: str, api: tweepy.API, csv_path: Path) -> None:
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.read_csv("./data/user_list.csv.default")
    response = api.search_users(q=query)[0]
    print(response.name, response.screen_name)
    print(response.description)
    if input("YES or NO : ").lower() in ["yes", "y"]:
        name = input("registratoin name :")
        row = {"user_id": response.screen_name, "name": name, "since_id": 1}
        df = df.append(row, ignore_index=True)
        df.to_csv(csv_path, index=False)


def registration_hashtag(hashtag: str, api: tweepy.API, csv_path: Path) -> None:
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.read_csv("./data/hashtag_list.csv.default")
    results = api.search_tweets(hashtag + " -filter:retweets")
    print(f"found {len(results)} tweet")

    if input("YES or NO : ").lower() in ["yes", "y"]:
        name = input("registratoin name :")
        row = {"hashtag": hashtag, "name": name}
        df = df.append(row, ignore_index=True)
        df.to_csv(csv_path, index=False)


def register():
    with open("./config.yaml") as f:
        config = yaml.safe_load(f)

    auth = tweepy.OAuthHandler(config["API_KEY"], config["API_KEY_SECRET"])
    auth.set_access_token(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])
    tweet_api = tweepy.API(auth)

    while True:
        print(
            "please enter search query(hashtag) if you use UserID, please enter '--user'"
        )
        print("if you want to finish, please enter '--exit'")
        query = input("QUERY : ")

        if query == "--exit":
            break
        elif query.startswith("--user"):
            query = input("USER :")
            registration_user(query, tweet_api, Path(config["user_list_data"]))
        else:
            registration_hashtag(query, tweet_api, Path(config["hashtag_list_data"]))


if __name__ == "__main__":
    register()
