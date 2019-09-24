"""
Chris Bogart
Dec 2018

This program converts unimported posts to csv format for discoursedb import

Usage:
    To import posts from a subreddit:
        python json2csv.py --limit <max records to import> -S <forum list> -A <author list>
"""
import json
import os
# command line interface
import click
# import your own config file, see example_config.py
import config
from reddit import Reddit
import mysql.connector
import time
import pytz
import csv
from datetime import datetime
from pymongo import MongoClient

tz = pytz.timezone('UTC')

def get_discoursedb_post_set(db):
    connection = mysql.connector.connect(
            host= config.discoursedb_host_for_sql_db,
            user= config.discoursedb_user_for_sql_db,
            password= config.discoursedb_password_for_sql_db,
            database= db
        );
    cur = connection.cursor(dictionary=True);
    
    cur.execute("""select entity_source_id from data_source_instance where entity_source_descriptor = 'reddit#id#POST';""")
    keys = {row["entity_source_id"] for row in cur.fetchall()}
    
    return keys

def posts2csv(post_f, authors=None, subreddits=None, seen_posts = set(), verbose=True, limit = 1000):
    reddit = Reddit(MongoClient('mongodb://127.0.0.1:27017')["reddit"])
    
    subreddits = [reddit.get_subreddit(s) for s in subreddits]
    authors = [reddit.get_user(a) for a in authors]

    subredditset = set()

    # subreddit info doesn't seem to have the "subreddit_id".   To do : get that with r/subreddit/<name>/about
    # for now, use subreddit name as forum identifier
    csvp = csv.writer(post_f)
    csvp.writerow("id,replyto,username,user_annotation_flairtext,annotation_over18,annotation_score,forum,discourse,title,when,dataset_file,post".split(","))

    for subreddit in subreddits:
        print(subreddit.name)
        postids = set(subreddit.post_ids) - seen_posts
        for i, idd in enumerate(postids):
            post = subreddit.post(idd)
            if i%1000 == 999: print("post",i,"of",len(postids),limit,"to go")
            if "selftext" not in post or post["selftext"] == "": continue   # Skip URL-only posts
            if "subreddit" not in post:
                print("No subreddit in post " + post["id"])
                continue
            if post["id"] in seen_posts: continue
            csvp.writerow([post["id"],None,post["author"],post["author_flair_text"],str(post["over_18"]),str(post["score"]),
                           post["subreddit"],"Reddit",post["title"],
                           datetime.fromtimestamp(post["created"], tz).isoformat(),
                           "reddit",post.get("selftext",post["url"])])
            limit -= 1
            if limit == 0: return

    for author in authors:
        print(author.name)
        postids = set(author.post_ids) - seen_posts
        for i,post in enumerate([author.post(id) for id in postids]):
            if i%1000 == 999: print("post",i,"of",len(postids),limit,"to go")
            if "selftext" not in post or post["selftext"] == "": continue   # Skip URL-only posts
            if "subreddit" not in post:
                print("No subreddit in post " + post["id"])
                continue
            if post["id"] in seen_posts: continue
            csvp.writerow([post["id"],None,post["author"],post["author_flair_text"],str(post["over_18"]),str(post["score"]),
                           post["subreddit"],"Reddit",post["title"],
                           datetime.fromtimestamp(post["created"], tz).isoformat(),
                           "reddit",post.get("selftext",post["url"])])
            limit -= 1
            if limit == 0: return
        


@click.command()
@click.option( '-l', '--limit', type=int, default=1000)
@click.option( '-A', '--author-list', 'author_list', type=click.File("r"))
@click.option( '-d', '--discoursedb-database', 'ddb_db', type=str)
@click.option( '-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
@click.option( '-o', '--posts-file', 'posts_file', type=click.File("w"))
def main(author_list, subreddit_list, limit, posts_file, ddb_db):
    try:
        seen_posts = set(get_discoursedb_post_set("discoursedb_ext_" + ddb_db))
    except Exception as e:
        print(type(e), e)
        seen_posts = set()
    if author_list is not None:
        authors = [str(a).strip().split("/")[-1] for a in author_list if a.strip() != ""]
    else: authors = []
    if subreddit_list is not None:
        subreddits = [str(s).strip().split("/")[-1] for s in subreddit_list if s.strip() != ""]
    else: subreddits = []
    posts2csv(posts_file, authors, subreddits, seen_posts, limit=1000, verbose=True)

if __name__ == '__main__':
    main()

