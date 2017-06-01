# Rss_Digest

This is a python script that is designed to take a json of rss feed locations and a bloom filter. 
You run it, and it gives you a since-last-time's worth of new feed activity. 

You'll need to add another file `authinfo.json`. It has three fields. `email_pass`, `email_from`, and `email_to`. These do what you'd expect.

## Resources to consider
[Parsing Example](https://siongui.github.io/2015/03/03/go-parse-web-feed-rss-atom/)
[Golang Email](https://golang.org/pkg/net/smtp/)

## Directions to consider
1) bloom filter detection of duplicates 
- Will need to build, not a big problem
- needs to be serializable.

2) run occasionally on a cronjob, yaml/toml config file and stable output.?
3) run continuously waiting for either a timer or a web request, take a config 
file and stable output, but also accept json for subs and maybe also serialize a 
big, global rss feed out of it?
4) twitter integration? May be a challenge.

## Alternate direction:

Rss->Pinboard. Maybe daily check frequency, any new items are just sent over, 
after whatever detection scheme is used (maybe just datetime?). Figure out API, 
would be like email but no notifications and silent unless checked. Probably also
want to consider aggressive tagging so as to be able to filter/delete as wanted.
