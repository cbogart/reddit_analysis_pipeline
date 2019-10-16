#!/bin/bash
# Run from the root directory of reddit_analysis_pipeline
echo `date` >> logs/crawl_log.txt
echo ============================= >> logs/crawl_log.txt
for forum in resources/subreddit_groups/*.txt
do
    pipenv run python src/crawler/crawl_reddit.py -d reddit -S $forum >> logs/crawl_log.txt
done
