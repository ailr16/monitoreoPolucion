import urllib3

try:
	url = "https://www.google.com"
	urllib3.urlopen(url)
	status = "Connected"
	
except:
	status = "Not Connected"
	
print(status)
