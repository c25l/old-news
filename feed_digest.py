
# coding: utf-8

import feedparser
import xml.etree.ElementTree as etree
import time
import smtplib
import email
import urllib
import json
import twitter

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


def feedtime (feed):
    if 'published' in feed:
        return feed.published_parsed
    elif 'updated' in feed:
        return feed.updated_parsed
    elif 'created' in feed:
        return feed.created_parsed
    else:
        return False
    
    
def parse_feeds(opml_loc):
    try:
        opml = []
        for feed in etree.parse(opml_loc).getroot()[1]:
            try:
                opml.extend(parse_item_or_list(feed))
            except:
                pass
        feeds = [ feedparser.parse(feed) for feed in opml]
        return [{'title': feed_title(feed), 'entries': recent_items_for_feed(feed.entries)} for feed in feeds] 
    except:
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

def send_email(title, body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title 
        msg['From'] = setup['email_dest']
        msg['To'] = setup['email_dest']
        html = str(body)
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
        s = smtplib.SMTP_SSL('smtp.gmail.com',465)
        s.login(setup['email_dest'], setup['email_pass'])
        s.sendmail(setup['email_dest'], setup['email_dest'], msg.as_string())
        s.quit()
        return 1
    except:
        return 0

    
def feeds_to_html(feeds):
    outstr="<body>"
    for x in feeds:
        if x['entries']:
            outstr+="<h3>"+x['title']+"</h3><br>"
            for y in x['entries']:
                outstr+="<a href=" + y['link'] +">"+y['title']+"</a><br>" + y['summary']+ "<br><br>" 
            outstr+="<hr>"
    return outstr+"</body>"


def main():
    setup=json.load(open('feed_digest.json','r'))
    send_email(get_weather(setup['weather_api_key'],
                           setup['weather_location']), 
               feeds_to_html(parse_feeds(setup['opml_location'])))
    
    
if __name__ == "__main__":
    main()

