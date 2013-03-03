import supybot.conf as conf
import supybot.utils as utils
import supybot.ircdb as ircdb
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.dbi as dbi

from random import choice

class Donair(callbacks.Plugin):
    """
    zoia serves up some of Halifax's finest gastronomic treats
    """

    class DB(plugins.DbiChannelDB):
        class DB(dbi.DB):
            class Record(dbi.Record):
                __fields__ = [
                    'donair'
                ]
            def add(self, donair, **kwargs):
                record = self.Record(donair=donair, **kwargs)
                return super(self.__class__, self).add(record)

    def __init__(self, irc):
        self.__parent = super(Donair, self)
        self.__parent.__init__(irc)
        self.db = plugins.DB(self.name(), {'flat': self.DB})()

    def _donair(self, channel):
        result = [r.donair for r in self.db.select(channel, lambda x: True)]
        result.sort()
        return result

    def add(self, irc, msg, args, channel, donair):
        """
        add a new donair to the list
        """

        if donair in self._donair(channel):
            irc.error("I already know how to make that donair.", prefixNick=False)
        else:
            self.db.add(channel, donair)
            irc.reply("Operation succeeded. I now know how to make a %s." % donair, prefixNick=False)

    add = wrap(add, ['channeldb', 'text'])

    def remove(self, irc, msg, args, channel, donair):
        """
        remove a donair from the list
        """

        if not donair in self._donair(channel):
            irc.error("I don't even know how to make a %s" % donair, prefixNick=False)
        else:
            self.db.remove(channel, donair)
            irc.reply("Operation succeeded. I no longer know how to make a %s." % donair, prefixNick=False)

    remove = wrap(remove, ['channeldb', 'text'])

    def donair(self, irc, msg, args, channel, nick):
        """
        serves up one of Halifax's finest
        """

        donairs = self._donair(channel)
        if not donairs:
            irc.error("No one in %s has taught me any donairs" % channel, prefixNick=False)
        else:
            if not nick:
                nick = msg.nick

            donair = choice(donairs)
            irc.reply("wraps up a %s and sends it sliding down the counter to %s" % (donair, nick), action=True)

    donair = wrap(donair, ['channeldb', optional('text')])

Class = Donair
