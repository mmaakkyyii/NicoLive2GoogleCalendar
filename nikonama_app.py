from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import sys
import requests
import urllib.parse
import csv
from urllib import request
from bs4 import BeautifulSoup

DEBUG = False

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar(calendar_url):
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token/token.pickle'):
		with open('token/token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token/token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API
	timefrom=datetime.datetime.now().isoformat()+'Z'
	timeto= (datetime.datetime.now() + datetime.timedelta(days=60))
	timeto=timeto.isoformat()+'Z'
	if DEBUG==True:
		print(timefrom)
		print(timeto)
	events_result = service.events().list(calendarId=calendar_url,
										timeMin=timefrom,
										timeMax=timeto,
										singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])

	result=[]

	if not events:
		if DEBUG==True:
			print('No upcoming events found.')
	for event in events:
		try:
			start = event['start'].get('dateTime', event['start'].get('date'))
			start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S')
			if DEBUG==True:
				print(event)
				print(start, event['summary'])
			url=event['description']
			contentID=url[-11:]
			result.append(contentID)
			if DEBUG==True:
				print(contentID)
				print(event['start']['dateTime'])
				print(event['end']['dateTime'])
		except:
			print(event)
	return result



def add_event(title,contentId,start_time,end_time,cakendar_url):
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token/token.pickle'):
		with open('token/token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token/token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('calendar', 'v3', credentials=creds)

	event = {
		'summary': title,
		'location': '',
		'description': 'https://live2.nicovideo.jp/watch/'+contentId,
		'start': {
			'dateTime': start_time,
			'timeZone': 'Japan',
		},
		'end': {
		'dateTime': end_time,
		'timeZone': 'Japan',
		},
	}

	event = service.events().insert(calendarId=cakendar_url,
									body=event).execute()


def get_nicolive(data):#name,channelID,targets,q
	nicolive_API_endpoint="https://api.search.nicovideo.jp/api/v2/live/contents/search"
#	print(data[i][0])
	q_=data[3]
	q=urllib.parse.quote(q_)
	targets=data[2]

	fields='contentId,channelId,title,startTime,liveEndTime,description'
	filters_channelId='&filters[channelId][0]='+str(data[1])
	filters_liveStatus='&filters[liveStatus][0]=reserved' #enum('past','onair','reserved')

	_sort='-startTime'
	_context='nico live to google calender'
	_limit=str(10)

	url=nicolive_API_endpoint+'?q='+q+'&targets='+targets+'&fields='+fields+filters_channelId+filters_liveStatus+'&_sort='+_sort+'&_context='+_context+'&_limit='+_limit

	#print(url)
	r = requests.get(url)
	#print(r.json())
	return r.json()

def get_nicolive_from_title(title):#title of live
	nicolive_API_endpoint="https://api.search.nicovideo.jp/api/v2/live/contents/search"
	q=title
	targets='title'

	fields='contentId,channelId,title,startTime,liveEndTime'
	filters_channelId=''
	filters_liveStatus='&filters[liveStatus][0]=reserved' #enum('past','onair','reserved')

	_sort='-startTime'
	_context='nico live to google calender'
	_limit=str(10)

	url=nicolive_API_endpoint+'?q='+q+'&targets='+targets+'&fields='+fields+filters_channelId+filters_liveStatus+'&_sort='+_sort+'&_context='+_context+'&_limit='+_limit

	#print(url)
	r = requests.get(url)
	#print(r.json())
	return r.json()

def init():
	filename='channel_list/channel_list.csv'
	channel_list=[]
	with open(filename, newline='',encoding="utf-8_sig") as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			channel_list.append(row)
			if DEBUG==True:
				print(', '.join(row))

	MY_CALENDAR=''
	with open('url/MY_CALENDAR_URL.txt', 'r') as cal:
		MY_CALENDAR=str(cal.read())
		if DEBUG==True:
			print(MY_CALENDAR)
	setting=[channel_list,MY_CALENDAR]
	return setting


def main():
	setting=init()
	channel_list=setting[0]
	MY_CALENDAR=setting[1]

	scheduled_contentID=get_calendar(MY_CALENDAR)
	if DEBUG==True:
		print(scheduled_contentID)

	for ls in channel_list:
		if DEBUG==True:
			print(ls)
		schedule=get_nicolive(ls)
		try:
			for s in schedule['data']:
				if (s['contentId'] in scheduled_contentID):
					print(' -',s['contentId'],s['title'],s['startTime'],s['liveEndTime'])
				else:
					print(' @',s['contentId'],s['title'],s['startTime'],s['liveEndTime'])
					add_event(s['title'],s['contentId'],s['startTime'],s['liveEndTime'],MY_CALENDAR)
		except KeyError:
			print(schedule['meta'])
			print("KeyError")

def add_non_registered_schedule(title):
	setting=init()
	channel_list=setting[0]
	MY_CALENDAR=setting[1]

	scheduled_contentID=get_calendar(MY_CALENDAR)
	if DEBUG==True:
		print(scheduled_contentID)

	schedule=get_nicolive_from_title(title)
	if DEBUG==True:
		print(schedule)
	try:
		data=schedule['data'][0];
		if (data['contentId'] in scheduled_contentID):
			print(' -',data['contentId'],data['title'],data['startTime'],data['liveEndTime'])
		else:
			print(' @',data['contentId'],data['title'],data['startTime'],data['liveEndTime'])
			add_event(data['title'],data['contentId'],data['startTime'],data['liveEndTime'],MY_CALENDAR)
	except KeyError:
		print(schedule['meta'])
		print("KeyError")

def usage():
	print('.py            | nomal')
	print('.py -d         | debug on')
	print('.py -u \'url\' | add schedule of the url')
	print('.py -d \'url\' | add schedule of the url with debug')


if __name__ =='__main__':
	args = sys.argv
	if len(args)==1:
		main()
	elif len(args)==2:
		option=args[1]
		if option == '-d':
			DEBUG=True
			main()
		else:
			usage()
	elif len(args)==3:
		option=args[1]
		url=args[2]
		if option=='-u':
			r=request.urlopen(url)
			soup=BeautifulSoup(r,'html.parser')
			title=soup.find('p',class_='___title___1aYd0').span.text
			print(title)
			add_non_registered_schedule(title)
		elif option=='-d':
			DEBUG=True
			r=request.urlopen(url)
			soup=BeautifulSoup(r,'html.parser')
			title=soup.find('p',class_='___title___1aYd0').span.text
			print(title)
			add_non_registered_schedule(title)
		else:
			usage()
	else:
		usage()


