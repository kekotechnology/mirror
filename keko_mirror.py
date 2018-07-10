import flask
from flask import render_template
import feedparser
import random
import time
import json
import urllib
import datetime
import uuid
from flask_oauthlib.client import OAuth
import config

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
APP.debug = True
APP.secret_key = 'development'
OAUTH = OAuth(APP)
MSGRAPH = OAUTH.remote_app(
    'microsoft', consumer_key=config.CLIENT_ID, consumer_secret=config.CLIENT_SECRET,
    request_token_params={'scope': config.SCOPES},
    base_url=config.RESOURCE + config.API_VERSION + '/',
    request_token_url=None, access_token_method='POST',
    access_token_url=config.AUTHORITY_URL + config.TOKEN_ENDPOINT,
    authorize_url=config.AUTHORITY_URL + config.AUTH_ENDPOINT)

@APP.route('/login')
def login():
    """Prompt user to authenticate."""
    flask.session['state'] = str(uuid.uuid4())
    return MSGRAPH.authorize(callback=config.REDIRECT_URI, state=flask.session['state'])

@APP.route('/login/authorized')
def authorized():
    """Handler for the application's Redirect Uri."""
    if str(flask.session['state']) != str(flask.request.args['state']):
        raise Exception('state returned to redirect URL does not match!')
    response = MSGRAPH.authorized_response()
    flask.session['access_token'] = response['access_token']
    return flask.redirect('/')

@APP.route('/graphcall')
def graphcall():
    #Confirm user authentication by calling Graph and displaying some data.
    todaydate = datetime.datetime.now().date().strftime('%Y/%m/%d')
    endpoint = 'me/calendarview?StartDateTime=2018-04-24T01:00:00&EndDateTime=2018-04-24T23:59:00'
    print(endpoint)
    #endpoint = 'me/calendarview' + '?StartDateTime=' + todaydate + '&EndDateTime=' + todaydate
    headers = {'SdkVersion': 'sample-python-flask',
               'x-client-SKU': 'sample-python-flask',
               'client-request-id': str(uuid.uuid4()),
               'return-client-request-id': 'true'}
    outlookdata = MSGRAPH.get(endpoint, headers=headers).data['value']

    meetings = []

    for ev in outlookdata:
      event_item = ev['subject']
      meetings.append(event_item)

    #graphdata = outlookdata['value'][1]['subject']
    return flask.render_template('graphcall.html',
                                 graphdata=meetings,
                                 endpoint=config.RESOURCE + config.API_VERSION + '/' + endpoint,
                                 sample='Flask-OAuthlib')

@MSGRAPH.tokengetter
def get_token():
    """Called by flask_oauthlib.client to retrieve current access token."""
    return (flask.session.get('access_token'), '')

#THE ACTUAL PAGE
@APP.route('/')
def index():
  #weather
  weather_url = 'http://api.openweathermap.org/data/2.5/weather?appid=e422a718b0bc6e6633fe25bc86c5ee57&units=metric&q=london,uk'
  weather_list = json.load(urllib.request.urlopen(weather_url))
  weather_description = weather_list['weather'][0]['description']
  weather_icon = weather_list['weather'][0]['icon']
  weather_icon_url = '/static/images/weather/' +  weather_icon + '.svg'
  temperature = int(weather_list['main']['temp'])
  date="{:%A %d %B %Y}".format(datetime.datetime.now().date())
  
  #quote
  random_quote = random.choice(open('quotes.txt').readlines())

  #Meetings list
  todaydate = datetime.datetime.now().date().strftime('%Y/%m/%d')
  endpoint = 'me/calendarview?StartDateTime=2018-04-24T01:00:00&EndDateTime=2018-04-24T23:59:00'
  print(endpoint)
  #endpoint = 'me/calendarview' + '?StartDateTime=' + todaydate + '&EndDateTime=' + todaydate
  headers = {'SdkVersion': 'keko-mirror',
              'x-client-SKU': 'keko-mirror',
              'client-request-id': str(uuid.uuid4()),
              'return-client-request-id': 'true'}
  outlookdata = MSGRAPH.get(endpoint, headers=headers).data['value']
  
  meetings = []

  for ev in outlookdata:
      event_item = ev['start']['dateTime'][11:][:-11] + ' - ' + ev['end']['dateTime'][11:][:-11] + '  ' + ev['subject']
      meetings.append(event_item)

  #Tube URL
  tube_url="https://api.tfl.gov.uk/Line/Mode/tube/Status?app_id=2a69bd54&app_key=f7dba5cab390f9e3c86e188408255324"
  tube_status = json.load(urllib.request.urlopen(tube_url))

  tube = []

  for s in tube_status:
    tube_item = s['id'] + ' - ' + s['lineStatuses'][0]['statusSeverityDescription']
    #if 'Good Service' not in tube_item:
    tube.append(tube_item.title())

  #BBC News feed
  bbcfeedurl = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"
  bbcfeed = feedparser.parse(bbcfeedurl)
  news = []

  for i in range(8):
  	item = bbcfeed['items'][i]['title']
  	news.append(item)

  return render_template('index.html', temp=temperature, date=date, cal=meetings, news=news, quote=random_quote, tube=tube, weathericon=weather_icon_url)

APP.run(host='0.0.0.0', debug=True)

"""app.secret_key = 'development'
OAUTH = OAuth(app)
MSGRAPH = OAUTH.remote_app(
    'microsoft',
    consumer_key=config.CLIENT_ID,
    consumer_secret=config.CLIENT_SECRET,
    request_token_params={'scope': config.SCOPES},
    base_url=config.RESOURCE + config.API_VERSION + '/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=config.AUTHORITY_URL + config.TOKEN_ENDPOINT,
    authorize_url=config.AUTHORITY_URL + config.AUTH_ENDPOINT)"""


"""quotedata= json.load(urllib.request.urlopen("http://quotes.rest/qod.json?category=management"))
quote = quotedata['contents']['quotes'][0]['quote']
author = quotedata['contents']['quotes'][0]['author']
#author = "Voltaire"
desc=weather_description.capitalize()
#quote = 'Each player must accept the cards life deals him or her: but once they are in hand, he or she alone must decide how to play the cards in order to win the game.'
"""

#Calandar
"""
calurl = "https://calendar.google.com/calendar/ical/cg1207%40gmail.com/private-70f93b7a241a13d283be8909ec02c2c9/basic.ics"
c = Calendar(urllib.request.urlopen(calurl).read().decode('iso-8859-1'))
cal = c.events

meetings = []

for i in range(6):
  event = cal[i]
  meetings.append(event.begin)
"""


#condition_id = weather_main[:2] #remove day/night
  #condition_id = '09'
  #condition_type = {'01' : 'clear sky', '02' : 'few clouds', '03' : 'Scattered Clouds', '04' : 'broken clouds', '09' : 'Shower rain', '10' : 'Rain', '11' : 'Thunderstorm', '13' : 'snow', '50' : 'mist'}
  #condition_color = {'01' : '0.55,0.4', '02' : '0.4,0.45', '03' : '0.3,0.3', '04' : '0.2,0.25', '09' : '0.1,0.2', '10' : '0.1,0.1', '11' : '0.25,0.05', '13' : '0.25,0.15', '50' : 'mist'}
  #return (condition_type.get(condition_id, 0))
