#!/bin/bash
POSTSFILE=/usr2/Reddit/trash/tmp/posts`date +%Y%m%d_%H%M`.mattress.csv
echo "---------STARTING MATTRESS IMPORT----------" `date` 
python3.7 /usr2/Reddit/src/gen_ddb_csv.py -csv $POSTSFILE -l 500 -m reddit-mattress -d MattressReddit -S /usr2/Reddit/resources/subreddit_groups/forums_mattress.txt 
echo "--------IMPORTING----------" `date` 
cd /usr2/scratch/discoursedb_v09/discoursedb-core/discoursedb-io-csv
java -cp target/oneThreadedForumCsv-0.9-SNAPSHOT.jar:target/classes:target/dependency/* edu.cmu.cs.lti.discoursedb.io.csvimporter.CsvImportApplication $POSTSFILE posts --jdbc.database=discoursedb_ext_MattressReddit
echo "--------DONE----------" `date` 
