###
# Copyright (c) 2012, Jon Gorman
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###



import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf
import re 

filename = conf.supybot.directories.data.dirize('Greeter.db')
joinmsg = "Welcome to code4lib! Visit http://code4lib.org/irc to find out more about this channel.  Type @helpers #code4lib for a list of people in channel who can help."

# drawn in part from Herald and Seen
class GreeterDB(plugins.ChannelUserDB):
    def serialize(self, v):
        return [v]
    
    def deserialize(self, channel, id, L):
        return L[0]
    
    def add(self, channel, nick):
        self[channel, self.normalizeNick(nick)] = 1         

    def remove(self, channel, nick):
        del self[channel, self.normalizeNick(nick)]
        
    #might need a method to normalize all nicks in the db
    def normalizeNick(self, nick):
        normNick = re.sub('_*$',      '', nick) ;
        normNick = re.sub('_mtg$',    '', normNick)
        normNick = re.sub('_away$',   '', normNick)
        normNick = re.sub('_lunch$',  '', normNick)
        normNick = re.sub('_dinner$', '', normNick)
        normNick = re.sub('_break$',  '', normNick)
        normNick = re.sub('_supper$', '', normNick)
        return normNick

    def get(self,channel,nick):
        return self[channel,self.normalizeNick(nick)]
        
        
class Greeter(callbacks.Plugin):
    """This plugin should greet people in channel"""
    threaded = True

    def __init__(self, irc):
        # these two lines necessary or goes kabloomie
        self.__parent = super(Greeter, self)
        self.__parent.__init__(irc)
        self.db = GreeterDB(filename)

        # I should pull this out into supybot.conf
        # but nervous about having to alter the supybot.conf
        # just for this plugin
        # so...for short term ...

        c4lIgnoredNicks = []
        for ignore in c4lIgnoredNicks:
            self.db.add('#code4lib', ignore)
        
    def die(self):
        self.db.close()    

    def __remove(self, irc, channel, nicks):

        removedNicks = []
        badNicks     = []
        
        for nick in nicks:
            try:
                self.db.remove(channel,nick)
                removedNicks.append( nick )
            except KeyError:
                badNicks.append( nick )
                
        if len( badNicks ) > 0:
            irc.reply("Nicks not in database: " + ", ". join( badNicks) )

        if len( removedNicks ) > 0:
            irc.reply("Removed: " + ", ".join( removedNicks ))

    def __add(self, irc, channel, nicks):

        addedNicks = []
                
        for nick in nicks:
            self.db.add(channel,nick)
            addedNicks.append( nick )
            
        irc.reply("Added: " + ", ".join( addedNicks ))
            
                
    def greeter(self, irc, msg, args):
        """ if no commands, greet nick of caller. if args[0] is add orremove, try doing that action w/ nicks that follow (separated by a space) """

        channel = msg.args[0]
        
        #irc.reply("hello")

        # apparently having remove and add in their own defs
        # makes then "available" as their own plugins.  IE
        # @remove and @add, don't want that, so having the
        # @greeter part do the add/remove via private methods
        
        if len(args) == 0:
            if ircutils.strEqual(irc.nick, msg.nick):
                return # It's us
            irc.queueMsg(ircmsgs.privmsg(msg.nick, joinmsg))
            irc.noReply()
        elif args[0] == 'remove':
            self.__remove(irc, channel, args[1:])
        elif args[0] == 'add':
            self.__add(irc, channel, args[1:])

        else:
            # should see if htere's a way to trigger help message
            irc.reply(" I don't understand what you are asking ")
                                
            
    def doJoin(self, irc, msg):

        #irc.reply("hello")
        if ircutils.strEqual(irc.nick, msg.nick):
            return # It's us

        channel = msg.args[0]
        if channel != "#code4lib" and channel != "#jtgtestchannel":
            return
        
        #if self.db[channel, msg.nick] is None:
        try:
            self.db.get(channel, msg.nick)
        except KeyError:
            irc.queueMsg(ircmsgs.privmsg(msg.nick, joinmsg))
            irc.noReply()
            #self.db.add(channel, msg.nick)
            self.db.add(channel, msg.nick) 

            
Class = Greeter


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
