#!/bin/bash
mkdir -p /tmp
cd /usr/src/pipeline
POSTSFILE=/tmp/posts`date +%Y%m%d_%H%M`.csv
echo "---------STARTING----------" `date` 
python3.7 src/transporter/gen_ddb_csv.py -csv $POSTSFILE -l 500 -m reddit-mattress -d mattress -S /usr/src/pipeline/resources/subreddit_groups/forums_mattress.txt 
echo "--------IMPORTING----------" `date` 
cd /usr/src/pipeline/discoursedb/discoursedb-core/discoursedb-io-csv
java -cp target/oneThreadedForumCsv-0.9-SNAPSHOT.jar:target/classes:target/dependency/* edu.cmu.cs.lti.discoursedb.io.csvimporter.CsvImportApplication $POSTSFILE posts --jdbc.database=discoursedb_ext_mattress  
echo "--------DONE----------" `date` 
