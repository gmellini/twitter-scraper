#!/bin/bash
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
  rm -f ${LOG}.old
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
while read line; do
  ONE=$(echo ${line} | cut -f 1 -d ',' | tr -d +)
  TWO=$(echo ${line} | cut -f 2 -d ',')
  THREE=$(echo ${line} | cut -f 3 -d ',')
  echo "> New reply to tweet ${THREE} on ${ONE}"
  echo ">> link: ${TWO}"
  echo
done < <(cat ${LOG}.diff) 

rm -f ${LOG}.diff
echo "Bye!"
exit 0
