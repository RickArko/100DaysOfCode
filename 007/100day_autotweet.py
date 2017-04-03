import datetime
import os
import re
import sys

import requests
import pytz

from config import logging, api

tz = pytz.timezone('Europe/Amsterdam')
now = datetime.datetime.now(tz)
start = datetime.datetime(2017, 3, 29, tzinfo=tz)  # = PyBites 100 days :)
CURRENT_CHALLENGE_DAY = str((now - start).days).zfill(3)

LOG = 'https://raw.githubusercontent.com/pybites/100DaysOfCode/master/LOG.md'
LOG_ENTRY = re.compile(r'\[(?P<title>.*?)\]\((?P<day>\d+)\)')
REPO_URL = 'https://github.com/pybites/100DaysOfCode/tree/master/'


def get_log():
    return requests.get(LOG).text.split('\n')


def get_day_progress(html):
    lines = [line.strip()
             for line in html
             if line.strip()]

    for line in lines:
        day_entry = line.strip('|').split('|')[0].strip()
        if day_entry == CURRENT_CHALLENGE_DAY:
            return LOG_ENTRY.search(line).groupdict()


def create_tweet(m):
    ht1, ht2 = '#100DaysOfCode', '#Python'
    title = m['title']
    day = m['day']
    url = REPO_URL + day

    fmt = '{} - Day {}: {} {} {}'
    return fmt.format(ht1, day, title, url, ht2)


def tweet_status(tweet):
    try:
        api.update_status(tweet)
        logging.info('Posted to Twitter')
    except Exception as exc:
        logging.error('Error posting to Twitter: {}'.format(exc))


if __name__ == '__main__':
    import socket
    local = 'MacBook' in socket.gethostname()

    if local:
        log = os.path.basename(LOG)
        with open(log) as f:
            html = f.readlines()
    else:
        html = get_log()

    m = get_day_progress(html)
    if not m:
        logging.error('Error getting day progress from log')
        sys.exit(1)

    tweet = create_tweet(m)
    if local:
        logging.info('Local test: tweet to send: {}'.format(tweet))
    else:
        tweet_status(tweet)
