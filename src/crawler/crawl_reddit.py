"""
Xinru Yan
Sep 2018

This program collects reddit posts per user(author) or per subreddit
Data location:
    mongo Reddit collections: posts, users, subreddits, scrapedates

Usage:
    To collect posts by one user:
        python crawl_reddit.py -l 1000 -a USER_NAME
    To collect posts by multiple users:
        python crawl_reddit.py -l 1000 -a USER_NAME -a USERNAME
    To collect posts by subreddit:
        python crawl_reddit.py -l 1000 -s SUBR_NAME
    TO collect posts by multiple subreddits:
        python craw_reddit.py -l 1000 -s SUBR_NAME -s SUBR_NAME
    TO collect posts by multiple subreddits listed in a file:
        python craw_reddit.py -l 1000 -S SUBR_LISTING_FILE
"""
from psaw import PushshiftAPI
import json
import os
# prograss bar
from tqdm import tqdm
# command line interface
import click
# import your own config file, see example_config.py
import config
import time
from pymongo import MongoClient, ASCENDING, DESCENDING



api = PushshiftAPI()


class Data:
    def __init__(self):
        self.mongoc = MongoClient("mongodb://127.0.0.1:27017")
        self.db = self.mongoc["reddit"]
        self.scrapedates = self.db["scrapedates"]
        self.posts = self.db["posts"]
        #self.posts.create_index([("id", ASCENDING)])
        #self.posts.create_index([("subreddit", ASCENDING)])
        #self.posts.create_index([("author", ASCENDING)])
        #self.scrapedates.create_index([("author", ASCENDING)])
        #self.scrapedates.create_index([("subreddit", ASCENDING)])
        #self.scrapedates.create_index([("newest_time", ASCENDING)])

    def get_newest_time(self, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        if author:
            found = self.scrapedates.find_one({"author": author})
        elif subreddit:
            found = self.scrapedates.find_one({"subreddit": subreddit})
        if found is not None:
            return found["newest_time"]

        return 0

    def set_newest_time(self, newest_time, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        if author:
            self.scrapedates.replace_one({"author": author}, {"author": author, "newest_time": newest_time}, upsert=True)
        if subreddit:
            self.scrapedates.replace_one({"subreddit": subreddit}, {"subreddit": subreddit, "newest_time": newest_time}, upsert=True)


    def add_posts(self, posts, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        for post in posts:
            self.posts.replace_one({"id": post["id"]}, post, upsert=True)

class PostFinder:
    def __init__(self, limit, start, author=None, subreddit=None):
        self.limit = limit
        self.start = start
        self.author = author
        self.subreddit = subreddit
        self.result = iter([])

    def __call__(self):
        args = {'sort': 'asc',
                'sort_type': 'created_utc',
                'after': self.start,
                'limit': self.limit}
        if self.author:
            args['author'] = self.author
        if self.subreddit:
            args['subreddit'] = self.subreddit

        self.result = api.search_submissions(**args)

        return self

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.result)

    def __len__(self):
        return self.limit


def grab_more_posts(find_posts):
    posts = []
    newest_time = find_posts.start

    for post in find_posts():
        posts += [post.d_]
        if post.created_utc > newest_time:
            newest_time = post.created_utc

    return posts, newest_time


def pull_posts(limit, authors=None, subreddits=None, verbose=True):
    if authors is None:
        authors = []
    if subreddits is None:
        subreddits = []

    data = Data()

    for author in authors:
        posts, newest_time = grab_more_posts(PostFinder(limit, start=data.get_newest_time(author=author), author=author))
        data.add_posts(posts, author=author)
        data.set_newest_time(newest_time, author=author)
        print(f'Pulled {len(posts)} posts; last post pulled for author "{author}" was posted on {time.ctime(newest_time)}')

    for subreddit in subreddits:
        posts, newest_time = grab_more_posts(PostFinder(limit, start=data.get_newest_time(subreddit=subreddit), subreddit=subreddit))
        data.add_posts(posts, subreddit=subreddit)
        data.set_newest_time(newest_time, subreddit=subreddit)
        print(f'Pulled {len(posts)} posts; last post pulled for subreddit "{subreddit}" was posted on {time.ctime(newest_time)}')


@click.command()
@click.option('-l', '--limit', type=int, default=1000)
@click.option('-a', '--author', 'authors', type=str, multiple=True, default=[])
@click.option('-s', '--subreddit', 'subreddits', type=str, multiple=True, default=[])
@click.option('-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
@click.option('-A', '--author-list', 'author_list', type=click.File("r"))
def main(limit, authors, subreddits, author_list, subreddit_list):
    if author_list is not None:
        authors = list(authors)
        authors.extend([str(a).strip().split("/")[-1] for a in author_list if a.strip() != ""])
    if subreddit_list is not None:
        subreddits = list(subreddits)
        subreddits.extend([str(s).strip().split("/")[-1] for s in subreddit_list if s.strip() != ""])
    pull_posts(limit, authors, subreddits, verbose=True)


if __name__ == '__main__':
    main()

