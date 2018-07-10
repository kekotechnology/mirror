import flask
from flask import render_template
import feedparser
import random
import requests
import time
import json
import urllib
import datetime
import uuid

#from ics import Calendar
#import pytz
#from pytz import timezone
#from newsapi import NewsApiClient

"""
--Weather api call: http://api.openweathermap.org/data/2.5/weather?appid=e422a718b0bc6e6633fe25bc86c5ee57&q=east%20grinstead,uk
Conditions list found here: http://openweathermap.org/weather-conditions
Use on the first category

--Quotes--
Line per quote in quotes.txt. Line will be pulled randomly on load/every 30mins.

--Tube data--
https://api.tfl.gov.uk/Line/Mode/tube/Status?app_id=2a69bd54&app_key=f7dba5cab390f9e3c86e188408255324

Application ID: 2a69bd54 | Application Keys: f7dba5cab390f9e3c86e188408255324

--Reload--
Currently set in index.html meta content="1800" value in seconds.

--Calendar URL--
AppID: dmoeDVOF[sylCCA26059_@-
AppID: 0f756d8d-6e4f-4b28-805a-41d4e7a92a0e

https://outlook.office.com/api/v2.0/me/calendarview

https://calendar.google.com/calendar/ical/cg1207%40gmail.com/private-70f93b7a241a13d283be8909ec02c2c9/basic.ics
"""

APP = flask.Flask(__name__, template_folder='templates')

@APP.route('/')
def index():
  #weather
  weather_url = 'http://api.openweathermap.org/data/2.5/weather?appid=e422a718b0bc6e6633fe25bc86c5ee57&units=metric&q=london,uk'
  weather_request = requests.get(weather_url)
  weather_list = json.loads(weather_request.content.decode('utf-8'))
  weather_description = weather_list['weather'][0]['description']
  weather_icon = weather_list['weather'][0]['icon']
  weather_icon_url = '/static/images/weather/' +  weather_icon + '.svg'
  temperature = int(weather_list['main']['temp'])
  date="{:%A %d %B %Y}".format(datetime.datetime.now().date())
  
  #quote
  random_quote = random.choice(open('quotes.txt').readlines())

  #Tube URL
  tube_url="https://api.tfl.gov.uk/Line/Mode/tube/Status?app_id=2a69bd54&app_key=f7dba5cab390f9e3c86e188408255324"
  tube_request = requests.get(tube_url)
  tube_status = json.loads(tube_request.content.decode('utf-8'))

  tube = []

  for s in tube_status:
    tube_item = s['id'] + ' - ' + s['lineStatuses'][0]['statusSeverityDescription']
    if 'Good Service' not in tube_item:
        tube.append(tube_item.title())

  #BBC News feed
  bbcfeedurl = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"
  bbcfeed = feedparser.parse(bbcfeedurl)
  news = []

  for i in range(8):
  	item = bbcfeed['items'][i]['title']
  	news.append(item)

  return render_template('index2.html', temp=temperature, date=date, news=news, quote=random_quote, tube=tube, weathericon=weather_icon_url)

APP.run(host='0.0.0.0', debug=True)