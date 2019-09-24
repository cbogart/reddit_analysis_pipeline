# Reddit

## Overview

This is a Reddit data scraper and analyzer using [Content Word Filtering and Speaker Preference Model (CSM)](https://github.com/yohanjo/Dialogue-Acts)

Data are stored using MongoDB, [DiscourseDB](http://discoursedb.github.io), and ElasticSearch

Data and code related to paper **Using Functional Schemas to Understand Social Media Narratives** see *FunctionalSchemas* dir

Dependencies see *Pipfile*

## How to access Reddit API

Please click [here](https://www.reddit.com/wiki/api)

## docs

Detailed documentation for this project.

## src

Source code dir

## resources

### subreddit_groups

Groups of subreddits. Each group contains several subreddits regarding similar topics  and the subreddit names are stored in a txt file, one subreddit per line

## logs

Log files in txt.

## CSM

CSM results

## Citation
If you find the pipeline useful in your research, please consider citing our paper:

```
@inproceedings{yan-etal-2019-using,
    title = "Using Functional Schemas to Understand Social Media Narratives",
    author = "Yan, Xinru and Naik, Aakanksha and Jo, Yohan and Rose, Carolyn",
    booktitle = "Proceedings of the Second Workshop on Storytelling",
    month = aug,
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W19-3403",
    pages = "22--33",
    abstract = "We propose a novel take on understanding narratives in social media, focusing on learning {''}functional story schemas{''}, which consist of sets of stereotypical functional structures. We develop an unsupervised pipeline to extract schemas and apply our method to Reddit posts to detect schematic structures that are characteristic of different subreddits. We validate our schemas through human interpretation and evaluate their utility via a text classification task. Our experiments show that extracted schemas capture distinctive structural patterns in different subreddits, improving classification performance of several models by 2.4{\%} on average. We also observe that these schemas serve as lenses that reveal community norms.",
}
```

## Copyright and License

Copyright (C) 2018, Xinru Yan

All code found in this repository is licensed under GPL v3

    This system is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation, either version 3 of the License, or (at your
    option) any later version.
    
    This system is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
    Public License for more details.
    
    You should have received a copy of the GNU General Public License along
    with this system. If not, see <http://www.gnu.org/licenses/>.





