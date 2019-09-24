#!/bin/bash
# Run from the root directory of reddit_analysis_pipeline
echo `date` >> logs/crawl_log.txt
echo ============================= >> logs/crawl_log.txt
for forum in resources/subreddit_groups/*.txt
do
    python3.7 src/crawler/crawl_reddit.py -S $forum >> logs/crawl_log.txt
done
