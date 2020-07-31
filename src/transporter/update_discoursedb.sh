#!/bin/bash
mkdir -p /tmp
cd /pipeline
POSTSFILE=tmp/posts`date +%Y%m%d_%H%M`.csv
for forum in resources/subreddit_groups/forums_*.txt
do
    ddbname=`echo $forum | sed -e 's/.*\/forums_\(.*\)\.txt/\1/'`
    echo "---------STARTING----------" $ddbname $forum `date` >> logs/ddb_log.txt
    python3.7 src/transporter/gen_discoursedb_csv.py -o $POSTSFILE -d $ddbname -S $forum &>> logs/ddb_log.txt
    echo "--------IMPORTING----------" `date` >> logs/ddb_log.txt
    bash /pipeline/discoursedb/discoursedb-io-csv/import_posts $POSTSFILE discoursedb_ext_$ddbname &>> logs/ddb_log.txt
    #java -cp target/oneThreadedForumCsv-0.9-SNAPSHOT.jar:target/classes:target/dependency/* edu.cmu.cs.lti.discoursedb.io.csvimporter.CsvImportApplication $POSTSFILE posts --jdbc.database=discoursedb_ext_$ddbname
    echo "--------DONE----------" `date` >> logs/ddb_log.txt
done
