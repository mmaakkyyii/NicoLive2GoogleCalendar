import sys
import requests
import urllib.parse
import csv

data=[]
filename='data.csv'
with open(filename, newline='',encoding="utf-8_sig") as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		data.append(row)
		print(', '.join(row))

for i in range(len(data)):
	nicolive_API_endpoint="https://api.search.nicovideo.jp/api/v2/live/contents/search"
#	print(data[i][0])

	q_=data[i][3]
	q=urllib.parse.quote(q_)
	targets=data[i][2]

	fields='contentId,channelId,title,startTime,liveEndTime'
	filters_channelId='&filters[channelId][0]='+str(data[i][1])
	filters_liveStatus='&filters[liveStatus][0]=reserved' #enum('past','onair','reserved')

	_sort='-startTime'
	_context='nico live to google calender'
	_limit=str(10)

	url=nicolive_API_endpoint+'?q='+q+'&targets='+targets+'&fields='+fields+filters_channelId+filters_liveStatus+'&_sort='+_sort+'&_context='+_context+'&_limit='+_limit

	#print(url)
	r = requests.get(url)
	res=r.json()
	#print(res)
	try:
		num=(len(res['data']))
		for i in res['data']:
			print(i['title'],end=',')
			a=i['startTime']
			print(a,end=',')
			print(i['liveEndTime'])
	except KeyError:
		print(res['meta'])
		print("KeyError")

