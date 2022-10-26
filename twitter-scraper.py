#!/usr/bin/env python

"""
Author:  Giovanni merlos Mellini
License: GNU General Public License v3.0
         https://github.com/gmellini/twitter-scraper/blob/master/LICENSE

This script allows you to get a complete list of twitter threads replies 
so you can have a fast and complete view of complex threads even if you 
are not cited in all the tweet branches

Check https://github.com/gmellini/twitter-scraper to read more on this
  
= Twitter Access Tokens = 
Generate here
 https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html

and modify [ CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET ]

= LIMITATION =
Twitter search API only returns results from last 7 days. This means that 
search results are limited to last 7 days

= TWITTER-SCRAPER-PY =
twitter-scraper.py reads a text file fileed with tweets URL (one per line) in 
the following format https://twitter.com/<SCREEN_NAME>/status/<ID>
The script checks and writes to stdout any reply to the given tweet, keeping 
replies indentation.

Option -s gives a short output that can be useful to diff content between 
different iterations of the script; this way you can check for newer replies 
and notify.

usage: twitter-scraper.py -f file [-s]
Options:
-f  : name of the input file that contains twitter URLs (1 per line) in the following 
      format: https://twitter.com/<SCREEN_NAME>/status/<ID>
-s  : csv output; useful to diff content between different iterations of the script

= REQUIREMENTS =
The script is tested with python 2.7 and 3.6 on Ubuntu 18.04 and 18.10
- install required pip packages:
    # Python 2.7
    sudo pip install python-twitter
    sudo pip install pytz
    # Python 3
    sudo pip3 install python-twitter
    sudo pip3 install pytz
- modify your timezone to have local dates
    - Full list here: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    - Current: local_timezone = 'Europe/Rome'

= EXAMPLES =
$ ./twitter-scraper.py  -f tweet.list
[...]
$ ./twitter-scraper.py  -f tweet.list -s
[...]

= CREDITS = 
Based on the initial work made by @edsu
 https://gist.github.com/edsu/54e6f7d63df3866a87a15aed17b51eaf
"""

import sys
import getopt
import json
import time
import twitter
import re
import os.path
import locale
from os import environ as e
from datetime import datetime
from pytz import timezone
try:
    import urllib # python 2.7
except ImportError:
    import urllib.parse # python 3

################################################
# SET YOUR TWITTER KEYS/SECRETS
e["consumer_key"]="CONSUMER_KEY"
e['consumer_secret']="CONSUMER_SECRET"
e["access_token_key"]="ACCESS_TOKEN"
e['access_token_secret']="ACCESS_TOKEN_SECRET"
# SET TIMEZONE FOR OUTPUT
local_timezone = 'Europe/Rome'
################################################

# Global vars
t = twitter.Api(
    consumer_key=e["consumer_key"],
    consumer_secret=e["consumer_secret"],
    access_token_key=e["access_token_key"],
    access_token_secret=e["access_token_secret"],
    sleep_on_rate_limit=True
)

tweet_url = None
tweet_user = None
twitter_id = None
twitter_sceen_name = None
short_output = False

# True to have debug messages
debug = False

def print_usage():
    print ('usage: twitter-scraper.py -f file [-s]')
    print ('Options:')
    print ('-f\t: name of the input file that contains twitter URLs (1 per line) in the following format: https://twitter.com/<SCREEN_NAME>/status/<ID>')
    print ('-s\t: csv output; useful to diff content between different iterations of the script')

def get_tweets(filename):
    global twitter_id
    global twitter_sceen_name
    global tweet_url
    global short_output

    for line in open(filename):
        if not short_output: print('=========================================')
        line.strip()
        if not re.search('^#', line):
            m = re.search('https://twitter.com/(.*)/status/(.*)', line)
            if m:
                twitter_sceen_name = m.group(1)
                twitter_id = m.group(2)
            else:
        	    if not short_output: print('[WARNING] Malformed URL - Not scraping %s' % (line))
        	    continue
            twitter_json = '{"user":{"screen_name": "'+twitter_sceen_name+'"},"id": '+twitter_id+'}'
            tweet_url = 'https://twitter.com/%s/status/%s' % (twitter_sceen_name, twitter_id)
            if not short_output: 
                print('[INFO] Start scraping from tweet URL %s' % (tweet_url))
                print('')
            yield twitter.Status.NewFromJsonDict(json.loads(twitter_json))
        else:
            if not short_output: print('[INFO] Comment - %s' % (line))
            continue


def get_replies(tweet):
    global tweet_user
    global debug
    global short_output

    tweet_user = tweet.user.screen_name
    tweet_id = tweet.id
    max_id = None
    page_index = 0
    while True:
        page_index += 1
        try:
            term = "to:%s" % tweet_user
            if debug: print('[DEBUG] Search: term=%s since_id=%s max_id=%s count=100' % (term, tweet_id, max_id))
            replies = t.GetSearch(
                term=term,
                since_id=tweet_id,
                max_id=max_id,
                count=100,
            )
        except twitter.error.TwitterError as e:
            if not short_output: print('[WARNING] Caught twitter api error, sleep for 60s: %s', (e))
            time.sleep(60)
            continue
        
        if not replies:
            if debug: print('[DEBUG] Found no replies. Search continues...')
            if debug: print('-----------------------------------------')
            break
        
        for reply in replies:
            if reply.in_reply_to_status_id == tweet_id:
                if debug: print('[DEBUG] Reply found')
                yield reply
                # recursive magic to also get replies to the reply
                for reply_to_reply in get_replies(reply):
                    yield reply_to_reply
            max_id = reply.id
        
        max_id = reply.id - 1

        if len(replies) != 100:
            break

def main(argv):
    global tweet_url
    global twitter_id
    global short_output
    global local_timezone

    # Parse ARGV[]
    try:
        opts, args = getopt.getopt(argv, "hsf:")
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    find_f = False
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit(0)
        elif opt == '-f':
            file_in = arg
            find_f = True
        elif opt == '-s':
            short_output = True
    
    if find_f is False:
        print('[ERROR] Missing mandatory option -f')
        print('')
        print_usage()
        sys.exit(2)

    if not os.path.exists(file_in):
        print('[ERROR] File %s not exists' % (file_in))
        print('')
        print_usage()
        sys.exit(2)

    # Verify key/secrets
    if e["consumer_key"] == "CONSUMER_KEY" or e['consumer_secret'] == "CONSUMER_SECRET" or e["access_token_key"] == "ACCESS_TOKEN" or e['access_token_secret'] == "ACCESS_TOKEN_SECRET":
        print('[ERROR] It seems that Twitter key/secrets where not set.')
        print('\tGenerate here https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html and set to start playing')
        print('')
        print_usage()
        sys.exit(2)

    if short_output: print('date,reply,parent_thread');

    for tweet in get_tweets(file_in):
        if tweet_url is not None:
            tabs = ''
            last = None
            count = 0
            for reply in get_replies(tweet):
                j = json.loads(reply.AsJsonString())
                
                if int(reply.in_reply_to_status_id) == int(twitter_id):
                	tabs = ''
                elif int(reply.in_reply_to_status_id) == int(last):
                    tabs = '%s  ' % tabs
                else:
                    tabs = '%s\b\b' % tabs
                
                last = j['id']
                pre_human_date = j['created_at'].replace('+0000 ', '')
                human_date = datetime.strptime(pre_human_date, '%a %b %d %H:%M:%S %Y').replace(tzinfo=timezone('UTC')).astimezone(tz=timezone(local_timezone)).strftime('%d/%m/%Y %H:%M:%S')
                count += 1

                if not short_output: 
                    print('%s/----------------------------------' % (tabs))
                    print('%s| From:\t %s (@%s)' % (tabs, j['user']['name'], j['user']['screen_name']))
                    if debug: print('%s| Twitter date:\t %s' % (tabs, j['created_at']))
                    print('%s| Date:\t %s' % (tabs, human_date))
                    print('%s| URL:\t https://twitter.com/%s/status/%s' % (tabs, j['user']['screen_name'], j['id']))
                    print('%s| %s' % (tabs, j['text']))
                    print('%s\\----------------------------------' % (tabs))
                    print ('')

                if short_output: print('%s,https://twitter.com/%s/status/%s,%s' % (human_date, j['user']['screen_name'], j['id'], tweet_url))

                if debug: 
                    print('')
                    print('[DEBUG] status ID: %s' % (j['id']))
                    print('[DEBUG] in reply to: %s' % (j['in_reply_to_status_id']))
                    print('[DEBUG] JSON response:')
                    print(reply.AsJsonString())
            if not short_output: 
                print('')
                print('[INFO] Total replies: %s' % (count))
    
    if not short_output: print('=========================================')

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)
