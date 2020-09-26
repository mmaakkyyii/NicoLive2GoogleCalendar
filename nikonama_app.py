from __future__ import print_function
#import datetime
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
from datetime import datetime, timezone, timedelta

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
	timefrom=datetime.now().isoformat()+'+09:00'
	timeto= (datetime.now() + timedelta(days=60))
	timeto=timeto.isoformat()+'+09:00'
	print("start time to get calendar: ",end="")
	print(timefrom)
	if DEBUG==True:
		print("start time to get calendar: ",end="")
		print(timefrom)
		print("end time to get calendar: ",end="")
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
			start = datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S')
			if DEBUG==True:
				print(event)
				print(start, event['summary'])
			live_id=event['location']
			print(live_id)
			result.append(live_id)
			if DEBUG==True:
				print(contentID)
				print(event['start']['dateTime'])
				print(event['end']['dateTime'])
		except:
			print(event)
	return result

'''
title:カレンダーのタイトル[str]
description:説明 URLなど[str]
stat_time end_time:開始終了時間[datetime.datetime]
'''
def add_event(title,live_id,description,start_time,end_time,calendar_url):
	start_time=datetime.strftime(start_time, '%Y-%m-%dT%H:%M:%S')
	end_time=datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%S')

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
		'location': live_id,
		'description': description,
		'start': {
			'dateTime': start_time,
			'timeZone': 'Japan',
		},
		'end': {
		'dateTime': end_time,
		'timeZone': 'Japan',
		},
	}

	event = service.events().insert(calendarId=calendar_url,body=event).execute()

def add_linelive_event(title,contentId,start_time,end_time,calendar_url):
	add_event(title,contentId,contentId,start_time,end_time,calendar_url)

def add_nicolive_event(title,contentId,start_time,end_time,calendar_url):
	add_event(title,contentId,'https://live2.nicovideo.jp/watch/'+contentId,start_time,end_time,calendar_url)

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
	_limit=str(60)

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

def get_LINE_LIVE(ch_id):#data[live_id,title,start,end]
	url = 'https://live-api.line-apps.com/web/v4.0/channel/'+ch_id;
	r = requests.get(url).json()
	if DEBUG==True:
		print(r['upcomings'])
	try:
		prog=r['upcomings']['rows'][0]

		live_id=prog['id']
		title=prog['title']
		start_time=datetime.fromtimestamp(prog['startAt'],timezone(timedelta(hours=9)))
		finish_time=datetime.fromtimestamp(prog['finishAt'],timezone(timedelta(hours=9)))
		data={'live_id':live_id,'title':title,'start_time':start_time,'finish_time':finish_time}

		if DEBUG==True:
			print('title:',end='')
			print(title);
			print('startAt:',end='')
			print(start_time)
			print('finishAt:',end='')
			print(finish_time)

		return data
	except:
		return None



def init():
	nicolive_filename='channel_list/nicolive_channel_list.csv'
	nicolive_channel_list=[]
	with open(nicolive_filename, newline='',encoding="utf-8_sig") as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			nicolive_channel_list.append(row)
			if DEBUG==True:
				print(', '.join(row))

	linelive_filename='channel_list/linelive_channel_list.csv'
	linelive_channel_list=[]
	with open(linelive_filename, newline='',encoding="utf-8_sig") as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in spamreader:
			linelive_channel_list.append(row[1])
			if DEBUG==True:
				print(', '.join(row))
	print(nicolive_channel_list)
	print(linelive_channel_list)

	MY_CALENDAR=''
	with open('url/MY_CALENDAR_URL.txt', 'r') as cal:
		MY_CALENDAR=str(cal.read())
		if DEBUG==True:
			print(MY_CALENDAR)

	setting=[MY_CALENDAR,nicolive_channel_list,linelive_channel_list]
	return setting


def main():
	setting=init()
	MY_CALENDAR=setting[0]
	nicolive_channel_list=setting[1]
	linelive_channel_list=setting[2]

	scheduled_contentID=get_calendar(MY_CALENDAR)
	if DEBUG==True:
		print(scheduled_contentID)

	for ls in nicolive_channel_list:
		if DEBUG==True:
			print(ls)
		schedule=get_nicolive(ls)
		try:
			for s in schedule['data']:
				start_time=datetime.strptime(s['startTime'], '%Y-%m-%dT%H:%M:%S%z')
				end_time=datetime.strptime(s['liveEndTime'], '%Y-%m-%dT%H:%M:%S%z')
				if (s['contentId'] in scheduled_contentID):
					print(' -',s['contentId'],s['title'],start_time,end_time)
				else:
					print(' @',s['contentId'],s['title'],start_time,end_time)
					add_nicolive_event(s['title'],s['contentId'],start_time,end_time,MY_CALENDAR)
		except KeyError:
			print(schedule['meta'])
			print("KeyError")

	for ls in linelive_channel_list:
		if DEBUG==True:
			print(ls)
		schedule=get_LINE_LIVE(ls)
		if schedule==None:
			continue
		try:
			start_time=schedule['start_time']
			end_time=schedule['finish_time']
			if (str(schedule['live_id']) in scheduled_contentID):
				print(' -',schedule['live_id'],schedule['title'],start_time,end_time)
			else:
				print(' @',schedule['live_id'],schedule['title'],start_time,end_time)
				add_linelive_event(schedule['title'],schedule['live_id'],start_time,end_time,MY_CALENDAR)
		except KeyError:
			print("KeyError")


def add_non_registered_schedule(title):
	setting=init()
	nicolive_channel_list=setting[0]
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
			add_nicolive_event(data['title'],data['contentId'],data['startTime'],data['liveEndTime'],MY_CALENDAR)
	except KeyError:
		print(schedule['meta'])
		print("KeyError")

	linelive_schedule=get_LINE_LIVE('4785540')
	add_linelive_event(linelive_schedule['live_id'],linelive_schedule['title'],linelive_schedule['start_time'],linelive_schedule['finish_time'],MY_CALENDAR)


def usage():
	print('.py            | nomal')
	print('.py -d         | debug on')
	print('.py -l         | line line')
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
		if option == '-l':
			DEBUG=True
			linelive_schedule=get_LINE_LIVE('4785540')
			#title,contentId,start_time,end_time,calendar_url
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
		if option=='-y':
			r=request.urlopen(url)
			soup=BeautifulSoup(r,'html.parser')
			title=soup.find_all(content='title')
			print(title)
			#add_non_registered_schedule(title)
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


