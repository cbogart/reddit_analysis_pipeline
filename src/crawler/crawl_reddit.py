"""
Xinru Yan and Chris Bogart
July 2019

This program collects reddit posts and comments per subreddit

Usage:
    To collect posts by subreddit:
        python crawl_reddit.py -l 1000 -s SUBR_NAME -d DB_NAME
    To collect posts by multiple subreddits:
        python craw_reddit.py -l 1000 -s SUBR_NAME -s SUBR_NAME -d DB_NAME
    To collect posts by a list of subreddits:
        python crawl_reddit.py -d DB_NAME -S FILE_NAME
    To include comments: add -c
"""
from psaw import PushshiftAPI
import click
import time
from pymongo import MongoClient, ASCENDING, DESCENDING


api = PushshiftAPI()


class Data():
    def __init__(self, db):
        self.mongoc = MongoClient("mongodb://127.0.0.1:27017")
        self.db = self.mongoc[db]
        self.scrapedates = self.db["scrapedates"]
        self.posts = self.db["posts"]
        self.comments = self.db["comments"]

        self.posts.create_index([("id", ASCENDING)])
        self.posts.create_index([("subreddit", ASCENDING)])
        self.posts.create_index([("author", ASCENDING)])
        self.scrapedates.create_index([("author", ASCENDING)])
        self.scrapedates.create_index([("subreddit", ASCENDING)])
        self.scrapedates.create_index([("newest_time", ASCENDING)])
        self.comments.create_index([("id", ASCENDING)])
        self.comments.create_index([("subreddit", ASCENDING)])

    def get_newest_time_comments(self, subreddit):
        try:
            return self.scrapedates.find_one({"subreddit": subreddit}).get("newest_time_comments",0)
        except: 
            return 0

    def get_newest_time_posts(self, subreddit):
        try: 
            return self.scrapedates.find_one({"subreddit": subreddit}).get("newest_time",0)
        except: 
            return 0

    def set_newest_time(self, newest_time_posts, newest_time_comments, subreddit):
        self.scrapedates.replace_one({"subreddit": subreddit}, {"subreddit": subreddit, "newest_time": newest_time_posts, "newest_time_comments": newest_time_comments}, upsert=True)

    def add_posts(self, posts):
        for post in posts:
            self.posts.replace_one({"id": post["id"]}, post, upsert=True)

    def add_comments(self, comments):
        for comment in comments:
            self.comments.replace_one({"id": comment["id"]}, comment, upsert=True)

class ItemFinder:
    def __init__(self, itemtype, limit, start, subreddit):
        self.itemtype = itemtype  
        assert self.itemtype in ["posts","comments"]
        self.limit = limit
        self.start = start
        self.subreddit = subreddit
        self.result = iter([])

    def __call__(self):
        args = {'sort': 'asc',
                'sort_type': 'created_utc',
                'after': self.start,
                'limit': self.limit}
        args['subreddit'] = self.subreddit

        if self.itemtype == "posts":
            self.result = api.search_submissions(**args)
        elif self.itemtype == "comments":
            self.result = api.search_comments(**args)

        return self

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.result)

    def __len__(self):
        return self.limit

    def grab_more_items(self):
        items = []
        newest_time = self.start
    
        for item in self():
            items += [item.d_]
            if item.created_utc > newest_time:
                newest_time = item.created_utc
    
        return items, newest_time


def pull_posts(limit, database, subreddits, verbose=True):
    if subreddits is None:
        subreddits = []

    data = Data(database)

    for subreddit in subreddits:
        posts, newest_time_posts = ItemFinder("posts", limit, data.get_newest_time_posts(subreddit), subreddit).grab_more_items()
        comments, newest_time_comments = ItemFinder("comments", limit, data.get_newest_time_comments(subreddit), subreddit).grab_more_items()
        data.add_posts(posts)
        data.add_comments(comments)
        data.set_newest_time(newest_time_posts, newest_time_comments, subreddit)
        print(f'Last post pulled for subreddit "{subreddit}" was posted on {time.ctime(newest_time_posts)}; last comment was {time.ctime(newest_time_comments)}')


@click.command()
@click.option('-l', '--limit', type=int, default=1000)
@click.option('-s', '--subreddit', 'subreddits', type=str, multiple=True)
@click.option('-d', '--database', 'database', type=str)
@click.option('-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
def main(limit, subreddits, subreddit_list, database):
    if subreddit_list is not None:
        subreddits = list(subreddits)
        subreddits.extend([str(s).strip().split("/")[-1] for s in subreddit_list if s.strip() != ""])
    pull_posts(limit, database, subreddits, verbose=True)


if __name__ == '__main__':
    main()

