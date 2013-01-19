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
joinmsg = "Welcome to code4lib! Visit http://code4lib.org/irc to find out more about this channel.  Type @helpers for a list of people in channel who can help."

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
        normNick = re.sub('_*$','',nick) ;
        normNick = re.sub('_mtg$','',normNick)
        normNick = re.sub('_away$','',normNick)
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

    def die(self):
        self.db.close()    


        
    def greeter(self, irc, msg, args):
        """ if no commands, greet nick of caller. if args[0] is add/remove, try doing action w/ nicks that follo """

        channel = msg.args[0]
        
        #irc.reply("hello")
        if len(args) == 0:
            if ircutils.strEqual(irc.nick, msg.nick):
                return # It's us
            irc.queueMsg(ircmsgs.privmsg(msg.nick, joinmsg))
            irc.noReply()
        elif args[0] == 'remove':
            channel = msg.args[0]
            nicks = args[1:]
            removedNicks = []

            for nick in nicks:
                try:
                    self.db.remove(channel,nick)
                    removedNicks.append( nick )
                except KeyError:
                    #irc.queueMsg(nick + " was not in db ")
                    #irc.noReply()
                    irc.reply(nick + " was not in db ")
                    
            if len( removedNicks ) > 0:
                #irc.queueMsg("Removed " + ", ".join( removedNicks ))
                #irc.noReply()
                irc.reply("Removed " + ", ".join( removedNicks ))

        elif args[0] == 'add':
            addedNicks = []
            for nick in args[1:]:
                self.db.add(channel,nick)
                addedNicks.append( nick )

            irc.reply("Added " + ", ".join( addedNicks ))
            #irc.noReply()

        else:
            # should see if htere's a way to trigger help message
            irc.reply(" I don't understand what you are asking ")
            #irc.queueMsg(" I don't understand what you are asking ")
            #irc.noReply()
                    
            
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
