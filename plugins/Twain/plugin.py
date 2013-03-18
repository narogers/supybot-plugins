# coding=utf-8

import feedparser
import math
import os
import random
import re
import simplejson
import time
import string
import lxml
from os.path import join, abspath, dirname
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, StopParsing
from cgi import parse_qs
from datetime import date, datetime
from elementtidy import TidyHTMLTreeBuilder
from int2word import int2word
from random import randint, choice, seed
from urllib import quote, urlencode
from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from urlparse import urlparse
from threading import Timer
import csv

from supybot.commands import *
import supybot.callbacks as callbacks

class PollNotFoundException(Exception):
    pass


class Twain(callbacks.Privmsg):

    def twain(self,irc,msg,args):
        """
	Fetch a random Mark Twain quote from twainquotes.com
	"""

	base = 'http://www.twainquotes.com/'
	letter = random.choice(string.letter).upcase
	category_list = base + letter + '.html'

        soup = self._url2soup(category_list)
        categories = soup.find('table').first.find_all('a')
	category = random.choice(categories)['html']

	quote_url = base + category
	soup = self._url2soup(quote_url)
        quotes = soup.find_all('p')
        quote = quotes[randint(0, len(quotes)]
	
        irc.reply("%s" % (quote, quote.text.encode('utf8','ignore')))

Class = Twain
