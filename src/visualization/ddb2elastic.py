import sys
from datetime import datetime
import requests
import urllib
import urllib3
from requests.auth import HTTPBasicAuth
import json
import csv
import pdb

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = json.load(open("ddb2kib_config.json"))

class DiscourseDB:
    """Query DiscourseDB's REST interface and extract data.

    This assumes you've set a password on your account; if you are using
    Google to log in, this is *not* your google password, it's a separate
    DiscourseDB password feature.  See project "discoursedb-core/user-management"
    for tools for setting this password; currently only an admin may set
    or change passwords

    Example use is at the bottom of this file.  You must create a named
    selection in the data browser by hand, then this program can download
    the data.    
    """

    def __init__(self, user, password, service):
        self.user= user
        self.password = password
        self.service = service
        self.db = None

    def set_db(self, db=None):
        """Limit interface to a particular database; or set to None to query across databases"""
        self.db = db

    def _upload(self, endpoint, params={}, filename=None, fileparam="file"):
        assert filename is not None, "No upload file specified"
        basic = HTTPBasicAuth(self.user,self.password)
        files = {fileparam: open(filename,"rb")}
        return requests.post("%s/%s" % (self.service, endpoint), data = {}, auth=basic, verify=False, params=params, files=files, stream=True, headers={'Accept-Encoding': 'gzip, deflate, br', "user": config["username"}) 
        print("Posted")

    def _request(self, endpoint, params=None, parsejson = True):
        basic = HTTPBasicAuth(self.user,self.password)
        answer = requests.get("%s/%s" % (self.service, endpoint), auth=basic, verify=False, params=params)
        try:
            if parsejson:
                return json.loads(answer.text)
            else:
                return answer.text
        except Exception as e:
            print("Error querying discoursedb: ", e)
            print("    Server returned: ", answer.text)
            return answer.text 

    def cache_saved_queries(self):
        url = "browsing/prop_list?ptype=query" 
        self.queries = self._request(url)

    def list_saved_queries(self):
        self.cache_saved_queries()
        if self.db is None:
            return [entry["propName"] for entry in self.queries]
        else:
            return [entry["propName"] for entry in self.queries 
                  if json.loads(entry["propValue"])["database"] == self.db]

    def query_literal(self, q):
        """Given a query name, returns a string representing the named query"""
        self.cache_saved_queries()
        for entry in self.queries:
            if entry["propName"] == q:
                return entry["propValue"]

    def query_content(self, q):
        """Given a query name, returns a data structure representing the named query"""
        return json.loads(self.query_literal(q))

    def dump_query(self, q):
        """Given a query name, pretty-prints the query to stdout"""
        print(json.dumps(self.query_content(q), indent=4))
    
    def download_by_parts(self, query, tofile):
        q = query.copy()
        append = False
        rowcount = 0
        dps = q["rows"]["discourse_part"]
        print("Breaking query into", len(dps),"parts")
        for dp in dps:
           q["rows"]["discourse_part"] = [dp]
           print("Downloading part", json.dumps(dp))
           rc = self.download(q, tofile, append=append)
           rowcount += rc
           print("    Got",rc,"rows, for a total of", rowcount)
           append=True

    def upload_annotated(self, fromfile):
        """Upload the annotated file"""
        return self._upload("browsing/action/database/%s/uploadLightside" % (self.db.replace("discoursedb_ext_",""),),
                       filename=fromfile, fileparam = "file_annotatedFileForUpload")

    def download_for_annotation(self, query, tofile):
        """Run the query and download to a file

        May fail for very large queries, in which case use download_huge.
        If append=True, omit the header line, and append rather than write
        Return the number of rows retrieved"""

        data = self._request("browsing/action/downloadLightsideQuery/for_annotation.csv", 
                       params={"query": json.dumps(query)}, parsejson=False)
        outf = open(tofile, "wb")
        try:
            outf.write(data.encode("utf-8"))
        except Exception as e:
            print(e)
        try:
            return len(list(csv.reader(data.encode("utf-8")))) -1
        except Exception as e:
            print (e)
            return None

    def get_records(self, query):
        """Run the query and return the JSON results"""

        data = self._request("browsing/action/getQueryJson", 
                       params={"query": json.dumps(query)}, parsejson=True)
        return data

def denormalize(obj_list, sublist_key):
    for o in obj_list:
        if sublist_key in o and type(o[sublist_key]) is list:
            for sublist_item in o[sublist_key]:
                o1 = {k:o[k] for k in o}
                o1[sublist_key] = sublist_item
                yield o1
        else:
            yield o

def annotation_types(anns):
    return {ann["type"]  for ann in anns}

if __name__ == "__main__":
    print datetime.now().isoformat()
    interesting_annotations = set(["FT", "StorySchema"])
    ddb = DiscourseDB(config["user"], config["password"], config["service"])
    ddb.set_db(config["database"])
    #query = {"database":"EnviroRedditC","rows":{"discourse_part":[{"dpid":"13","name":"Green"},{"dpid":"20","name":"ZeroWaste"},{"dpid":"2","name":"environment"}]},"columns":["annotations","content","contributionId","contributor","discoursePartIds","discourseParts","parentId","startTime","title","type"]}
    query = {"database":"EnviroRedditC","rows":{"discourse_part":[{"dpid":"20","name":"ZeroWaste"}]},"columns":["annotations","content","contributionId","contributor","discoursePartIds","discourseParts","parentId","startTime","title","type"]}
    content = ddb.get_records(query)
    headers = {'Content-Type': 'application/json'}
    indexline = json.dumps({"index":{"_index":config["elasticsearch_index"]}})
    data = ""
    size = 0
    print datetime.now().isoformat()
    print "Retrieved from discoursedb", len(content["content"]), "records"
    datadump = open("datadump.txt","w")
    for item in content["content"]:
        anno_types = annotation_types(item.get("annotations",[]))
        if len(anno_types.intersection(interesting_annotations)) == 0:
            continue
        data = data + indexline + "\n"
        if "annotations" in item and len(item["annotations"]) > 0:
            for ann in item["annotations"]:
                if ann["type"] not in interesting_annotations:
                    continue
                range = [0, len(item["content"])]
                ann["text"] = ""
                if "range" in ann and "-" in ann["range"]:
                    range = [int(c)-1 for c in ann["range"].split("-")]
                    ann["text"] = item["content"][range[0]:range[1]]
                subkey = "annotation_" + ann["type"]
                if subkey not in item:
                    item[subkey] = []
                item[subkey].append(ann)
        data = data + json.dumps(item) + "\n"
        size += 1
        if size > 500:
            reply = requests.post(config["elasticsearch_url"] + config["elasticsearch_index"] + "/" + config["elasticsearch_mapping"] + "/_bulk?pretty", headers=headers, data=data)
            data = ""
            print("Imported ", size, " records to elasticsearch")
            size = 0
           
    datadump.write(data)
    reply = requests.post(config["elasticsearch_url"] + config["elasticsearch_index"] + "/" + config["elasticsearch_mapping"] + "/_bulk?pretty", headers=headers, data=data)
    print reply
    print reply.text[0:1000]
    print("Imported ", size, " records to elasticsearch")
    print datetime.now().isoformat()

    
