'''
Usage:
    python src/gen_annotations_from_CSM.py --seq CSM-enviroaction-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.8-N0.9-SEQ --alyz CSM/CSM*SEQ/analysis.txt --schemas CSM/CSM*SEQ/schemas.txt --anno working/annotations_csm.csv --index working/enviroaction_index.csv
'''
import csv
from itertools import groupby
import json
import datetime
import pandas as pd
import click
import ast
from collections import defaultdict


def iso8601time(t): return datetime.datetime.fromtimestamp(t).isoformat()


def load_topics(topicfile):
    """Load list of topics from a file with lines in the form FT3 <Topic description>"""
    topic_map = dict()
    for topicrow in open(topicfile):
        ft = int(topicrow.split(" ")[0].replace("F","").replace("T",""))
        description = topicrow.split(" ",1)[1]
        description = description.strip().replace(" ","_").replace("\n","")
        topic_map[ft] = description
    return topic_map


def load_schemas(schemafile):
    """Load list of schemas from a file with lines in the form: <Schemaname> FT1  FT3  FT7"""
    schema_map = defaultdict(set)
    for schemarow in open(schemafile):
        parts = schemarow.split()
        schemaname = parts[0]
        topics = [int(s.replace("F","").replace("T","")) for s in parts[1:]]
        for t in topics:
            schema_map[t].add(schemaname)
    return schema_map


@click.command()
@click.option('-s', '--seq', "seq_directory", type=str)
@click.option('-a', '--alyz', "analysis_file", type=str, default="analysis.txt")
@click.option('-c', '--schemas', "schemas_file", type=str, default="schemas.txt")
@click.option('-n', '--anno', "annofile", type=str, default="csm_annotated.csv")
@click.option('-x', '--index', 'indexfile', type=str)
def main(seq_directory, analysis_file, schemas_file, annofile, indexfile):
    """Read output of CSM model (https://github.com/yohanjo/dialogue-Acts)
       and create a CSV import file for discoursedb, that reassembles the text
       and annotates substrings of each posting by topic
 
       --seq:  the *_SEQ directory produced by dialogue-Acts
       --alyz: a file listing named foreground topics
       --schemas: a file listing schemas (schema_name, list of FTs)
       --anno: an output file to write to """
    # Read the named topics
    topicname = load_topics(analysis_file)
    schema_lookup = load_schemas(schemas_file)

    # Start writing the csv files
    csv_anno = csv.writer(open(annofile,"w"))
    anno_cols = "id,jsonAnnotations".split(",")
    csv_anno.writerow(anno_cols)

    current_post = ""
    anno_info = []
    post = ""
    df = pd.read_csv(indexfile)
    for seqid, rows in groupby(csv.DictReader(open(seq_directory + "/I1000-InstSentAssign.csv")), key=lambda row: row["SeqId"]):
        post = ""
        anno_info = []
        schemas = set()
        len_range = df.loc[df['SeqId'] == int(seqid), "IndexRange"].iloc[-1]
        post_len = ast.literal_eval(len_range)[1]
        for row in rows:
            tagged = row["TaggedText"]
            try:
                topic = topicname[int(row["FTopic"])]
            except Exception as e:
                print("No topic name found for topic: ", row["FTopic"], "seqid=", seqid, "text='", tagged, "' error=", type(e), e)
                continue
            if ":" in tagged:
                tagged = " ".join([t.split(":")[1] for t in tagged.split(" ")])
            else:
                print("ignoring this sentence because it belongs to UNKNOWN FT")
                continue
            if topic is not None:
                try:
                    range = df.loc[(df['InstNo'] == int(row['InstNo'])) & (df['SeqId'] == int(seqid)), "IndexRange"].iloc[0]
                except IndexError:
                    pass
                anno_info.append({
                    "annotation": "FT",
                    "features": [topic],
                     "offsets": [ast.literal_eval(range)[0], ast.literal_eval(range)[1]]
                })
                try:
                    schemas.update(schema_lookup[int(row["FTopic"])])
                except:
                    print("No schema name found for topic ", row["FTopic"], "text=", tagged)
            post = post + tagged + ".\n"

        for schema in schemas:
            anno_info.append({"annotation": "StorySchema", "features": [schema], "offsets": [0,post_len]})
        rec = { 
            "id": row["SeqId"],
            "post": post,
            "jsonAnnotations": json.dumps(anno_info),
        }
        csv_anno.writerow([rec.get(k,"") for k in anno_cols])


if __name__ == '__main__':
    main()
