#!/usr/bin/env python
# coding: utf-8

import feedparser
import xml.etree.ElementTree as etree
import time
import smtplib
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
    key = inf['title']+ "////" + inf['summary']
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


def feeds_to_org(feeds):
    outstr=""
    for x in feeds:
        if x['entries']:
            outstr+="*** "+x['title']+"\n"
            for y in x['entries']:
                outstr+="**** [[" + y['link'] +"]["+ y['title']+"]]\n"
    return outstr


def main():
    #setup=json.load(open(sys.argv[1],'r'))
    feeds=json.load(open(sys.argv[1],'r'))
    bloom=pb.BloomFilter(1000000)
    bloomloc=sys.argv[2]
    try:
        bloom=bloom.fromfile(open(bloomloc,'r'))
    except:
        print "starting over"
        pass
    out = "\n* " + datetime.datetime.today().strftime("%Y-%m-%d") + "\n"
    for x,y in feeds.iteritems():
        out += "** " + x + "\n"
        out += feeds_to_org(parse_feeds(y, bloom))
    with open("./Rss_digest.org", 'a') as outf:
        outf.write(out.encode('utf8'))
    bloom.tofile(open(bloomloc,'w'))

if __name__ == "__main__":
    main()
