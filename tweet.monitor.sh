#!/bin/bash

# Author:  Giovanni merlos Mellini
# License: GNU General Public License v3.0
#         https://github.com/gmellini/twitter-scraper/blob/master/LICENSE
#
# This script allows you to check and be notified about new twitter threads replies#
# Check https://github.com/gmellini/twitter-scraper to read more on this
#
# Put your tweets in tweet.list file or edit TWEETLIST var to change input file
# 
# = EXAMPLE =
# $ ./tweet.monitor.sh 
# === TWEET MONITOR ===
# Log file found, archiving...
# Executing ~/twitter-scraper/twitter-scraper.py...
# Checking for new tweets...
# Found  new replies
# > New reply to tweet https://twitter.com/benkow_/status/1085483319347867649 on 16/01/2019 14:23:07
# >> link: https://twitter.com/cyb3rops/status/1085527873610485760
#
# Bye!
#
# = CREDITS = 
# Based on the initial work made by @edsu
#  https://gist.github.com/edsu/54e6f7d63df3866a87a15aed17b51eaf

echo "=== TWEET MONITOR ==="

PWD=$(pwd)
SCRAPER=${PWD}/twitter-scraper.py
TWEETLIST=${PWD}/tweet.list
LOG=${PWD}/twitter-scraper.log

if [ -f ${LOG} ]; then
  echo "Log file found, archiving..."
  cp ${LOG} ${LOG}.old 
else
  echo "date,reply,parent_thread" > ${LOG}.old
fi

echo "Executing ${SCRAPER}..."
${SCRAPER} -f ${TWEETLIST} -s > ${LOG}
if [ $? -ne 0 ]; then
  echo "[ERROR] Error executing \"${SCRAPER} -f ${TWEETLIST}\" command"
  mv ${LOG}.old ${LOG}
  exit 1
fi

echo "Checking for new tweets..."
DIFF=$(diff -u ${LOG}.old ${LOG} | grep '^\+[0-9]' > ${LOG}.diff)
if [ $(cat ${LOG}.diff | wc -l) -eq 0 ]; then
  echo "Cannot find new replies"
  echo "Bye!"
  exit 0
fi

echo "Found ${res} new replies"
echo
CURL=$(which curl)
while read line; do
  ONE=$(echo ${line} | cut -f 1 -d ',' | tr -d +)
  TWO=$(echo ${line} | cut -f 2 -d ',')
  THREE=$(echo ${line} | cut -f 3 -d ',')
  echo "> New reply to tweet ${THREE} on ${ONE}"
  echo ">> link: ${TWO}"
  # check https://github.com/gmellini/twitter-scraper/issues/1
  if [ ! "A${CURL}" = "A" ]; then
    # Set API key and API secret key
    # https://developer.twitter.com/en/docs/basics/authentication/oauth-2-0/bearer-tokens
    APIKEY="YOUR_API_KEY"
    APISECRETKEY="YOUR_API_SECRET_KEY"
    TWEETID=$(echo $TWO | awk -F/ '{print $NF}')
    BEARER=$(${CURL} -X POST "https://api.twitter.com/oauth2/token" \
        -H "Content-Type: application/x-www-form-urlencoded;charset=UTF-8" \
        -u ${APIKEY}:${APISECRETKEY} \
        --data-urlencode "grant_type=client_credentials" 2> /dev/null \
        | grep -Po '"access_token":.*?[^\\]"}' \
        | sed s/^\"access_token\":\"// \
        | sed s/\"}$//)
    echo "---"
    TEXT=$(${CURL} --request GET \
        --url "https://api.twitter.com/1.1/statuses/show.json?id=${TWEETID}" \
        --header "authorization: Bearer ${BEARER}" \
        --header 'content-type: application/json' 2> /dev/null \
        | grep -Po '"text":.*?[^\\]",' \
        | head -1 \
        | sed s/^\"text\":\"// \
	| sed s/\",$//)
    echo -e $TEXT
    echo "---"
  else
    echo "[INFO] curl not installed, cannot get tweet content"
  fi
  echo
done < <(cat ${LOG}.diff) 

rm -f ${LOG}.diff
echo "Bye!"
exit 0
