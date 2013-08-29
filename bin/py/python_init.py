import urllib

f = urllib.urlopen('http://10.100.56.55:8090/httpclient.html','mode=193&username=none')
s = f.read()
f.close()
print s
