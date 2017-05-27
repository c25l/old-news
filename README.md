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