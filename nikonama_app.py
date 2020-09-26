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


######### Google Calendar ######################################

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

#return liveId list
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
start_time end_time:開始終了時間[datetime.datetime]
'''
def add_event_to_Google_Calendar(live_id,title,description,start_time,end_time,calendar_url):
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

##############################################################################3


class Program_info:
	def __init__(self,live_id,title,start,end):
		self.title=title
		self.live_id=live_id
		self.start_time=start
		self.end_time=end

	def show(self):
		print('title:'+str(self.title)+'live_id:'+str(self.live_id)+'start:'+str(self.start_time)+'end:'+str(self.end_time))


class Platform:
	def __init__(self,url,list_path):
		self.calendar_url=url
		self.channel_list=self.get_channel_list(list_path)
		self.scheduled_contentID_list=get_calendar(self.calendar_url)
		if DEBUG==True:
			print(self.scheduled_contentID_list)
	
	def check_id_in_list(self,live_id):
		if str(live_id) in self.scheduled_contentID_list:
			return False
		else:
			return True
	
	def update(self):
		program_list=[]
		for channel_search_info in self.channel_list:
			for l in self.get_from_api(channel_search_info):
				self.check_and_add(l)


	def check_and_add(self,live_info):
		if self.check_id_in_list(live_info.live_id):
			print(' @',live_info.live_id,live_info.title,live_info.start_time,live_info.end_time)
			self.add_event(live_info.live_id,live_info.title,live_info.start_time,live_info.end_time)
		else:
			print(' -',live_info.live_id,live_info.title,live_info.start_time,live_info.end_time)
	
	def get_channel_list(self,list_path):
		pass

	def get_from_api(self,channel_info):
		pass

	def add_event(self,live_id,title,start_time,end_time):
		print("in platfrom")
		add_event_to_Google_Calendar(live_id,title,live_id,start_time,end_time,self.calendar_url)


class NicoLive(Platform):
	def add_event(self,live_id,title,start_time,end_time):
		add_event_to_Google_Calendar(live_id,title,'https://live2.nicovideo.jp/watch/'+live_id,start_time,end_time,self.calendar_url)
	
	def get_from_api(self,channel_info):#name,channelID,targets,q
		nicolive_API_endpoint="https://api.search.nicovideo.jp/api/v2/live/contents/search"
	#	print(data[i][0])
		q_=channel_info[3]
		q=urllib.parse.quote(q_)
		targets=channel_info[2]

		fields='contentId,channelId,title,startTime,liveEndTime,description'
		filters_channelId='&filters[channelId][0]='+str(channel_info[1])
		filters_liveStatus='&filters[liveStatus][0]=reserved' #enum('past','onair','reserved')

		_sort='-startTime'
		_context='nico live to google calendar'
		_limit=str(60)

		url=nicolive_API_endpoint+'?q='+q+'&targets='+targets+'&fields='+fields+filters_channelId+filters_liveStatus+'&_sort='+_sort+'&_context='+_context+'&_limit='+_limit

		res = requests.get(url).json()
		program_info_list=[]
		if res['meta']['totalCount']>0:
			for r in res['data']:
				start_time=datetime.strptime(r['startTime'], '%Y-%m-%dT%H:%M:%S%z')
				end_time=datetime.strptime(r['liveEndTime'], '%Y-%m-%dT%H:%M:%S%z')
				program_info_list.append(Program_info(r['contentId'],r['title'],start_time,end_time))

		return program_info_list

	def get_live_from_url(self,title):
		nicolive_API_endpoint="https://api.search.nicovideo.jp/api/v2/live/contents/search"
		q=title
		targets='title'

		fields='contentId,channelId,title,startTime,liveEndTime'
		filters_channelId=''
		filters_liveStatus='&filters[liveStatus][0]=reserved' #enum('past','onair','reserved')

		_sort='-startTime'
		_context='nico live to google calendar'
		_limit=str(1)

		url=nicolive_API_endpoint+'?q='+q+'&targets='+targets+'&fields='+fields+filters_channelId+filters_liveStatus+'&_sort='+_sort+'&_context='+_context+'&_limit='+_limit

		#print(url)
		res = requests.get(url)
		r=res.json()['data'][0]
		start_time=datetime.strptime(r['startTime'], '%Y-%m-%dT%H:%M:%S%z')
		end_time=datetime.strptime(r['liveEndTime'], '%Y-%m-%dT%H:%M:%S%z')
		return Program_info(r['contentId'],r['title'],start_time,end_time)
	
	def get_channel_list(self,list_path):
		nicolive_channel_list=[]
		with open(list_path, newline='',encoding="utf-8_sig") as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
			for row in spamreader:
				nicolive_channel_list.append(row)
				if DEBUG==True:
					print(', '.join(row))
		return nicolive_channel_list


class LineLive(Platform):
	def add_event(self,live_id,title,start_time,end_time):
		add_event_to_Google_Calendar(live_id,title,live_id,start_time,end_time,self.calendar_url)

	def get_from_api(self,channel_info):
		program_info_list=[]
		url = 'https://live-api.line-apps.com/web/v4.0/channel/'+channel_info;
		res = requests.get(url).json()

		try:
			if DEBUG==True:
				print(res['upcomings'])
			for r in res['upcomings']['rows']:
				start_time=datetime.fromtimestamp(r['startAt'],timezone(timedelta(hours=9)))
				finish_time=datetime.fromtimestamp(r['finishAt'],timezone(timedelta(hours=9)))
				program_info_list.append(Program_info(r['id'],r['title'],start_time,finish_time))

				if DEBUG==True:
					print('id:',end='')
					print(r['id']);
					print('title:',end='')
					print(r['title']);
					print('startAt:',end='')
					print(start_time)
					print('finishAt:',end='')
					print(finish_time)

			return program_info_list
		except:
			print("in LineLive get_from_api")
			return None

	def get_channel_list(self,list_path):
		linelive_channel_list=[]
		with open(list_path, newline='',encoding="utf-8_sig") as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
			for row in spamreader:
				linelive_channel_list.append(row[1])
				if DEBUG==True:
					print(', '.join(row))
		return linelive_channel_list


class YoutubeLive(Platform):
	def add_event(self,live_id,title,start_time,end_time):
		add_event_to_Google_Calendar(live_id,title,live_id,start_time,end_time,self.calendar_url)


def get_my_calendar():
	with open('url/MY_CALENDAR_URL.txt', 'r') as cal:
		MY_CALENDAR=str(cal.read())
		if DEBUG==True:
			print(MY_CALENDAR)
		return MY_CALENDAR

def main():
	MY_CALENDAR=get_my_calendar()

	nicolive = NicoLive(MY_CALENDAR,'channel_list/nicolive_channel_list.csv')
	linelive = LineLive(MY_CALENDAR,'channel_list/linelive_channel_list.csv')

	nicolive.update()
	linelive.update()


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
			MY_CALENDAR=get_my_calendar()
			nicolive = NicoLive(MY_CALENDAR,'channel_list/nicolive_channel_list.csv')

			r=request.urlopen(url)
			soup=BeautifulSoup(r,'html.parser')
			title=soup.find('p',class_='___title___1aYd0').span.text
			print(title)
			nicolive.check_and_add(nicolive.get_live_from_url(title))
		elif option=='-y':
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


