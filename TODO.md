Dockers
 - [x] controller            volume
 - [x] mongo
 - [x] discoursedb           volume
 - [x] discoursedb_mysql
 - [ ] ddb_browser
 - [ ] brat                  volume
 - [ ] elasticsearch
 - [ ] kibana
 - [ ] timeline_browser

Crawler
   - [x] Set up mongo and crawler dockers
   - [x] crawler docker has the script directories in it
   - [x] test that I can run it by hand
   - [x] crontab on crawler scrapes and writes to mongo
   - [x] test that it is working, fresh from docker-compse up
   - [ ] External script to show status of mongo scrape

Transporter
   - [x] set up discoursedb docker
   - [ ] (README) Script to configure discoursedb username, mysql root user, certificates
   - [ ] add csv importer java to server docker
   - [ ] add config file for forums -> mongo, discoursedb, elasticsearch vizhtml
   - [ ] add update_discoursedb.sh on schedule
   - [ ] set up browser docker, point to discoursedb docker
   - [ ] External script to show status of discoursedb database

Analyzer
   * add CSM and analyzer scripts to controller
   * base or incremental extract py  (on controller)
   * CSM runner
   * Splitter
   * annotation importer
   * Add incremental export/analyzsis/import to crontab
   
Visualizer
   * Add Elasticsearch, Kibana, and Timeline dockers
   * Create incremental export-to-elasticsearch
   * Crontab trigger export
   * Create configuration script for elastic, timeline
	* set 25000 record limit
        * add index by startTime as needed
        * create new viewer html for different datasets

Common Configuration Files
   * Forum.txt files in resources
   * Crontab file in resources with all schedules
   * Viz configuration scripts in src/visualizer

Tie together
   * Create Master activity log for:
        * total crawled records per subreddit
        * ddb imported records per subreddit
        * ddb exported records per subreddit
        * CSM runs
        * ddb exported annotations per subreddit
        * elasticsearch loads per forum
   * Add remodel script
        * dump all discoursedb records
        * run csm differently
        * clear annotations from discoursedb
        * reimport 
        * clear elasticsearch
        * reimport ddb -> elasticsearch

