import urllib
import time
import re
import os
import elasticsearch
import eatiht.v2 as v2


es = elasticsearch.Elasticsearch()

# Going through all the files in a directory and extracting title
for file_name in os.listdir('.'):
    if os.path.isfile(file_name) and "html" in file_name :
        print file_name
        file=open(file_name, 'r')
        regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
        title = regex.search(file.read())
        if title:
            title = title.group(1)
            body = v2.extract("file:///Users/Yash/www.digitalocean.com/community/tutorials/"+file_name)
            if body:
                result = es.index(index='digitalocean', doc_type='article', body={
                    'body': body,
                    'title':title
                })
                print result

            else:
                print "Error at " + file_name
#
# urllib.open()
#
# with open('digital_ocean.json', 'w') as f:
#     json.dump(article, f)
