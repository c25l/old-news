
# coding: utf-8

import feedparser
import xml.etree.ElementTree as etree
import time
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib
import json
import twitter
import sys
import datetime
import dateutil.parser

def parse_item_or_list(either):
    if 'xmlUrl' in either.attrib:
        return [either.attrib['xmlUrl']]
    else:
        return [x.attrib['xmlUrl'] for x in either]
    return 0


def recent_items_for_feed(feed):
    if len(feed)>0 and feedtime(feed[0]): 
        return [feed_info(x) for x in feed if recent(x)]
    elif len(feed)>0:
        return [feed_info(feed[0])]

    
def feed_title(feed):
    if 'feed' in feed and 'title' in feed.feed:
        return feed.feed.title
    return "No title!"


def feed_info(feed):
    return {'title':feed.title, 'summary':feed.summary, 'link':feed.link}


def recent(feed):
    return time.mktime(time.localtime()) - time.mktime(feedtime(feed)) < 60*60*26

def recent_tweet(tweet):
    tdiff = time.mktime(datetime.datetime.now().timetuple()) - time.mktime(dateutil.parser.parse(tweet['created_at']).timetuple())
    return tdiff < 60*60*26

def feedtime (feed):
    if 'published' in feed:
        return feed.published_parsed
    elif 'updated' in feed:
        return feed.updated_parsed
    elif 'created' in feed:
        return feed.created_parsed
    else:
        return False
    
    
def parse_feeds(feed_uris):
    try:
        feeds = [ feedparser.parse(feed) for feed in feed_uris]
        return [{'title': feed_title(feed), 'entries': recent_items_for_feed(feed.entries)} for feed in feeds] 
    except:
        print('feed parse failure')
        return []
    
    
def get_weather(apikey, location):
    try:
        f = urllib.request.urlopen('http://api.wunderground.com/api/'+apikey+'/geolookup/forecast/q/'+location+'.json')
        json_string = f.read().decode('utf-8')
        parsed = json.loads(json_string)['forecast']['simpleforecast']['forecastday'][0]
        f.close()
        return str(parsed['date']['yday']) + ": "+ parsed['conditions']+ ", "+parsed['high']['celsius'] +"/"+parsed['low']['celsius']
    except:
        return str(time.localtime().tm_yday) + ": weather error" 

def send_email(title, body, setup):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title 
        msg['From'] = "\"Old News\" <" +setup['email_dest']+">"
        msg['To'] = setup['email_dest']
        html = str(body)
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
        s = smtplib.SMTP_SSL('smtp.gmail.com',465)
        s.login(setup['email_dest'], setup['email_pass'])
        s.sendmail(setup['email_dest'], setup['email_dest'], msg.as_string())
        s.quit()
        return True
    except:
        print('email failure? ', sys.exc_info())
        return False

    
def feeds_to_html(feeds):
    outstr="<body>"
    for x in feeds:
        if x['entries']:
            outstr+="<h3>"+x['title']+"</h3><br>"
            for y in x['entries']:
                outstr+="<a href=" + y['link'] +">"+y['title']+"</a><br>" + y['summary'][:500]+ "<br><br>\n" 
            outstr+="<hr>"
    return outstr+"</body>"


def twitter_to_html(tweets):
    outstr="<body> Twitter: <br>\n"
    for x in tweets:
        outstr+= "<h4><img src=\""+x['image']+"\"> @"+x['screen_name']+ "  " + x['user'] + "<br></h4>\n"
        outstr+= x['text'] + " <br><br>"
    return outstr + "</body>\n"

def get_twitter(setup):
    try:
        twit = twitter.Twitter(auth=twitter.OAuth(setup['twitter_access_token'],
                                                  setup['twitter_access_secret'],
                                                  setup['twitter_consumer_key'],
                                                  setup['twitter_consumer_secret']))
        return [{"time": x['created_at'], 
                 "text": x['text'], 
                 "user": x['user']['name'], 
                 "image": x['user']['profile_image_url'], 
                 "screen_name": x['user']['screen_name']}  
                for x in twit.statuses.home_timeline(count=40) if recent_tweet(x)]
    except:
        print("twitter error", sys.exc_info())
        return []


def main():
    setup=json.load(open('feed_digest.json','r'))
    send_email(get_weather(setup['weather_api_key'],
                           setup['weather_location']), 
               feeds_to_html(parse_feeds(setup['feeds'])) +
               twitter_to_html(get_twitter(setup)),
               setup)
    
if __name__ == "__main__":
    main()

