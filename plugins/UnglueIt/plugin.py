from supybot.commands import *
import supybot.callbacks as callbacks

import urllib

from lxml.html import fromstring

class UnglueIt(callbacks.Privmsg):

    def unglueing(self, irc, msg, args):
        """See how UnglueIt campaigns are faring
        """
        html = urllib.urlopen("https://unglue.it/campaigns/ending").read()
        doc = fromstring(html)
        result = []

        for div in doc.xpath('.//div[@class="listview book-list"]'):
            title = div.xpath('string(.//div[@class="title"])').strip()
            current, goal = [e.text for e in div.xpath(".//span/b")]
            result.append("%s - %s/%s" % (title, current, goal))
        irc.reply(" ; ".join(result))

Class = UnglueIt
