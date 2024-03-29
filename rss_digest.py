#!/usr/bin/env python
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
import sys
import pybloom as pb
import datetime
import dateutil.parser

def parse_item_or_list(either):
    if 'xmlUrl' in either.attrib:
        return [either.attrib['xmlUrl']]
    else:
        return [x.attrib['xmlUrl'] for x in either]
    return 0

def bloom_detect(x, bloom):
    inf=feed_info(x)
    key = inf['link'] #inf['title']+ "////" + inf['summary']
    if key not in bloom:
        bloom.add(key)
        return inf

def unseen_items_for_feed(feed, bloom):
    if len(feed)>0:
        return [z for z in [bloom_detect(x,bloom) for x in feed] if z]
    elif len(feed)>0:
        return [feed_info(feed[0])]


def feed_title(feed):
    if 'feed' in feed and 'title' in feed.feed:
        return feed.feed.title
    return "No title!"


def feed_info(feed):
    return {'title':feed.title, 'summary':feed.summary, 'link':feed.link}


def parse_feeds(feed_uris,bloom):
        feeds = [ feedparser.parse(feed) for feed in feed_uris]
        return [{'title': feed_title(feed), 'entries': unseen_items_for_feed(feed.entries, bloom)} for feed in feeds]



def send_email(title, body, setup):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = "\"Rss Digest\" <" +setup['email_from']+">"
    msg['To'] = setup['email_to']
    html = body.encode('utf-8', 'ignore')
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    s = smtplib.SMTP_SSL('smtp.gmail.com',465)
    s.login(setup['email_from'], setup['email_pass'])
    s.sendmail(setup['email_from'], setup['email_to'], msg.as_string())
    s.quit()
    print "sent email"
    return True


def feeds_to_html(feeds):
    outstr=""
    for x in feeds:
        if x['entries']:
            outstr+="<h2>"+x['title']+"</h2><br>"
            for y in x['entries']:
                outstr+="<a href=" + y['link'] +">"+y['title']+"</a><br>\n" + y['summary'] + "\n<hr>\n"
            outstr+="<hr>"
    return outstr


def main():
    setup=json.load(open(sys.argv[1],'r'))
    feeds=json.load(open(sys.argv[2],'r'))
    bloom=pb.BloomFilter(1000000)
    bloomloc=sys.argv[3]
    try:
        bloom=bloom.fromfile(open(bloomloc,'r'))
    except:
        print "starting over"
        pass
    z = ""
    for x,y in feeds.iteritems():
        temp_title ="<h1>" + x + "</h1><br>\n "
        temp_feeds = feeds_to_html(parse_feeds(y, bloom))
        if len(temp_feeds)>0:
            z += temp_title+temp_feeds
        print x, len(temp_feeds)
    if len(z) > 0:
        send_email("RSS digest",
                   "<body>\n" + z + "</body>",
                   setup)
    bloom.tofile(open(bloomloc,'w'))

if __name__ == "__main__":
    main()
