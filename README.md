# Twitter Scraper
This script allows you to 
* **get a complete list of twitter thread replies** so you can have a fast and complete view of complex threads
* **check for new replies and get notified about it** using the csv output to diff between scheduled iteration of the script (example coming)

## Twitter Access Tokens
Twitter's API doesn't allow you to get all the replies to a particular tweet, but you can use it to search for replies to a given tweet and replies to any reply as well.

Before start playing with ```twitter-scraper.py``` you need your Twitter access tokens (keys/secrets).

Generate here https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html

## Limitation
Twitter search API only returns results from last 7 days. This means that __search results are limited to last 7 days__

## twitter-scraper.py
```twitter-scraper.py``` reads a text file fileed with tweets URL (one per line) in the following format 
```https://twitter.com/<SCREEN_NAME>/status/<ID>```

The script checks and writes to stdout any reply to the given tweet, keeping replies indentation.

Option ```-s``` gives a short output that can be useful to diff content between different iterations of the script; this way you can check for newer replies and notify.

```$ ./twitter-scraper.py -h
usage: twitter-scraper.py -f file [-s]
Options:
-f  : name of the input file that contains twitter URLs (1 per line) in the following format: https://twitter.com/<SCREEN_NAME>/status/<ID>
-s  : csv output; useful to diff content between different iterations of the script
```
## Requirements
The script is tested with python 2.7 and 3.6 on Ubuntu 18.04 and 18.10 

To start playing with ```twitter-scraper.py```:
* install required pip packages:
```
# Python 2.7
sudo pip install python-twitter
sudo pip install pytz
# Python 3
sudo pip3 install python-twitter
sudo pip3 install pytz
```
* adapt global vars; find&replace following placeholders:
```
CONSUMER_KEY
CONSUMER_SECRET
ACCESS_TOKEN
ACCESS_TOKEN_SECRET
```
* modify your timezone to have local dates
  * Full list here: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
  * Current: ```local_timezone = 'Europe/Rome'```

## Examples
```
$ ./twitter-scraper.py  -f tweet.list
[...]
=========================================
[INFO] Start scraping from tweet URL https://twitter.com/benkow_/status/1085483319347867649

/----------------------------------
| From:	 Jesse V. Burke (@Jesse_V_Burke)
| Date:	 16/01/2019 14:01:07
| URL:	 https://twitter.com/Jesse_V_Burke/status/1085522335095054336
| @benkow_ Benkow I have slides analyzing bulehero probably 6+ months ago. DM me let’s chat about this c2
\----------------------------------

/----------------------------------
| From:	 Benkøw moʞuƎq (@benkow_)
| Date:	 16/01/2019 12:17:21
| URL:	 https://twitter.com/benkow_/status/1085496220183945216
| A lot of web vulns / BF  behind that binary (looks like a worm)
\----------------------------------

  /----------------------------------
  | From:	 Benkøw moʞuƎq (@benkow_)
  | Date:	 16/01/2019 12:20:55
  | URL:	 https://twitter.com/benkow_/status/1085497120726097921
  | also Eternalblue
  \----------------------------------
[...]
$ ./twitter-scraper.py  -f tweet.list -s
date,reply,parent_thread
16/01/2019 14:01:07,https://twitter.com/Jesse_V_Burke/status/1085522335095054336,https://twitter.com/benkow_/status/1085483319347867649
16/01/2019 12:17:21,https://twitter.com/benkow_/status/1085496220183945216,https://twitter.com/benkow_/status/1085483319347867649
16/01/2019 12:20:55,https://twitter.com/benkow_/status/1085497120726097921,https://twitter.com/benkow_/status/1085483319347867649
[...]

```
## Credits
Based on the initial work made by @edsu
https://gist.github.com/edsu/54e6f7d63df3866a87a15aed17b51eaf
