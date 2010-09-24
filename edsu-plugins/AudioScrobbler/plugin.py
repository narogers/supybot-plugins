# -*- coding: utf-8 -*-

from os.path import join, dirname, abspath
from urllib import urlencode, quote, unquote
from urllib2 import urlopen
from sgmllib import SGMLParser
from random import randint, random
from xml.etree import ElementTree as ET
import simplejson

from supybot.commands import *
import supybot.conf as conf
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class AudioScrobbler(callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        self.__parent = super(AudioScrobbler, self)
        self.__parent.__init__(irc)
        #self.db = plugins.DB(self.name(), {'flat': self.DB})()
        #users_file = join(dirname(abspath(__file__)), 'users.json')
        self.users_file = conf.supybot.directories.data.dirize('AudioScrobbler.json')
        try:
            f = open(self.users_file)
            self.users = simplejson.load(f)
            f.close()
        except IOError, e:
            self.log.warning(str(e))
            self.users = []
        self.users.sort()
    
        self.nickmap = dict(
          # last.fm username = 'IRC nick',
            leftwing = 'mjgiarlo',
            DataGazetteer = 'pmurray',
            LTjake = 'bricas',
            moil = 'gsf',
            rtennant = 'royt',
            inkdroid = 'edsu',
            inkcow = 'rsinger',
            roblivian = 'robcaSSon',
            mdxi = 'sboyette',
            bsadler = 'bess',
            jaydatema = 'jdatema',
            jfrumkin = 'jaf',
            ryanwick = 'wickr',
            ranginui = 'rangi',
            mangrue = 'jtgorman',
            dys = 'MrDys',
            bosteen = 'BenO',
            tomkeys = 'madtom',
        )
        self.reverse_nickmap = dict((v,k) for k, v in self.nickmap.iteritems())

    def get_songs(self,username):
        import feedparser
        import socket
        socket.setdefaulttimeout(60)
        url = 'http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.rss'
        songs = []
        rss = feedparser.parse(url % username)
        for entry in rss.entries:
            song = entry.title.replace(u" – ", u' : ')
            songs.append(song.encode('utf8', 'ignore'))
        return songs

    def randtune(self,irc,msg,args):
        """Return a random song that someone in #code4lib listened to recently 
        """
        for user in shuffle(self.users):
            self.log.info(user)
            songs = self.get_songs(user)
            if len(songs) > 0:
                irc.reply(songs[0])
                return

    def tunes(self,irc,msg,args):
        """<user>
        See what <user> last listened to
        """
        username = ''.join(args)
        if not username:
            username = msg.nick
        username = self.reverse_nickmap.get(username, username)
        songs = self.get_songs(username)
        if len(songs) > 0:
            irc.reply(songs[0])
        else:
            irc.reply("i dunno what %s last listened to" % username)

    def alltunes(self,irc,msg,args):
        """<user>
        See the full list of tunes user listened to.
        """
        username = ''.join(args)
        if not username:
            username = msg.nick
        username = self.reverse_nickmap.get(username, username)
        songs = self.get_songs(username)
        if len(songs) > 0:
            irc.reply(' || '.join(self.get_songs(username)))
        else:
            irc.reply('i dunno any songs %s has listened to' % username)

    def blockparty(self,irc,msg,args,all):
        """        
        See what people in the group are listening to
        """
        channel = msg.args[0]

        if all == 'all' or not irc.isChannel(channel):
            show_all = True
        else:
            show_all = False

        tunes = [] 
        for user in self.users:
            nick = self.nickmap.get(user, user)
            if show_all or nick in irc.state.channels[channel].users:
                songs = self.get_songs(user)
                if len(songs) > 0:
                    tunes.append("%s: %s" % (nick, songs[0]))
        irc.reply('; '.join(tunes))

    blockparty = wrap(blockparty, [optional('text')])

    def _usersave(self):
        f = open(self.users_file, 'w')
        simplejson.dump(self.users, f, indent=2)
        f.close()

    def add(self,irc,msg,args):
        """<user>[,<user>...]
        Add one or more users to the blockparty
        """
        for user in args:
            # in case commas were used instead of spaces
            for u in user.split(','):
                if u not in self.users:
                    self.users.append(u)
        self._usersave()
        irc.reply(','.join(args) + " just moved in across the street")

    def remove(self,irc,msg,args):
        """<user>[,<user>...]
        Remove one or more users from the blockparty
        """
        for user in args:
            # in case commas were used instead of spaces
            for u in user.split(','):
                self.users.remove(u)
        self._usersave()
        irc.reply(','.join(args) + " was just evicted")

    def favs(self,irc,msg,args):
        """<user>
        Get user's favorite artists
        """
        username = ''.join(args)
        if not username:
            username = msg.nick
        username = self.reverse_nickmap.get(username, username)
        try:
            favs = self._favs(username)
            irc.reply(', '.join(favs).encode('utf8', 'ignore'))
        except:
            irc.reply('no such user "%s" or last.fm is on the fritz' % username)

    def _favs(self, username):
        url = "http://ws.audioscrobbler.com/1.0/user/%s/topartists.txt" % username
        favs = []
        for row in urlopen(url):
            favs.append(row.split(',')[2].strip("\n"))
            if len(favs) >= 20:
                break
        return favs

    def taste(self, irc, msg, args, username):
        """<user>
        Get the top tags of a user's fav artists
        """
        if not username:
            username = msg.nick
        username = self.reverse_nickmap.get(username, username)

        try:
            favs = self._favs(username)
        except:
            irc.reply('no such user "%s" or last.fm is on the fritz' % username)

        fav_tags = {}
        for fav in favs:
            try:
                for tag in self._tags(fav):
                    tag = tag.split(':')[0]
                    fav_tags.setdefault(tag, 0)
                    fav_tags[tag] += 1
            except:
                self.log.info("No tags found for %s" % fav)
        
        sorted_fav_tags = sorted(fav_tags, key=fav_tags.get, reverse=True)[:20]
        tastes = ["%s: %s" % (w, fav_tags[w]) for w in sorted_fav_tags]
        irc.reply(', '.join(tastes).encode('utf8', 'ignore'))
    
    taste = wrap(taste, [optional('text')])

    def scrobblers(self,irc,msg,args):
        user_list = []
        for user in self.users:
            nick = self.nickmap.get(user)
            if nick:
                user_str = '%s (%s)' % (nick, user)
            else:
                user_str = '%s' % user
            user_list.append(user_str)
        if user_list:
            irc.reply("; ".join(user_list))
        else:
            irc.reply('none found')

    def recommend(self,irc,msg,args):
        artist = quote(' '.join(args))
        if artist.lower() == 'lightning%20bolt':
          irc.reply("I recommend you listen to something else...")
          return

        self.log.info(artist.lower())
        if (artist.lower() == 'motley%20crue'):
            irc.reply("No.")
            return

        url = 'http://ws.audioscrobbler.com/1.0/artist/%s/similar.xml' % artist
        try:
            response = urlopen(url)
        except:
            irc.reply("no such artist or last.fm is on the fritz")
            return
            
        tree = ET.parse(response)
        root = tree.getroot()
        names = []
        for name in root.findall('.//name'):
            names.append(name.text)
        irc.reply(', '.join(names).encode('utf8','ignore'))

    def weeklies(self,irc,msg,args):
      """<user>
      Get a weekly top 10 for a last.fm user
      """
      if len(args) == 0:
        irc.reply("forgot username")
        return

      user = args[0]
      url = 'http://ws.audioscrobbler.com/1.0/user/%s/weeklytrackchart.xml' % user
      try:
          response = urlopen(url)
      except:
          irc.reply("no such user or last.fm is on the fritz")
          return
          
      tree = ET.parse(response)
      root = tree.getroot()
      tracks = []
      for track in root.findall('.//track'):
          artist = track.find('.//artist').text
          title = track.find('.//name').text
          count = track.find('.//playcount').text
          tracks.append("%s - %s [%s]" % (artist, title, count))
      irc.reply('; '.join(tracks).encode('utf8','ignore'))

    def tags(self,irc,msg,args):
        artist = quote(' '.join(args))
        try:
            tags = self._tags(artist)
            irc.reply(' ; '.join(tags).encode('utf8','ignore'))
        except:
            irc.reply("No tags found for %s" % ' '.join(args))

    def _tags(self, artist):
        url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml" % artist
        response = urlopen(url)
            
        tree = ET.parse(response)
        root = tree.getroot()
        tags = []
        for tag in root.findall('.//tag'):
            name = tag.find(".//name")
            count = tag.find(".//count")
            tags.append("%s: %s%%" % (name.text, count.text))
        return tags

    def topten(self,irc,msg,args):
        url = 'http://ws.audioscrobbler.com/1.0/group/code4lib/weeklytrackchart.xml'
        try:
            response = urlopen(url)
        except:
            irc.reply("d'oh can't get the weekly track chart :(")
            return
        tree = ET.parse(response)
        root = tree.getroot()
        tracks = []
        for track in root.findall('.//track'):
            artist = track.find('.//artist')
            name = track.find('.//name')
            tracks.append("%s:%s" % (artist.text.strip(), name.text.strip()))
        irc.reply(', '.join(tracks).encode('utf8','ignore'))

    def topten2(self,irc,msg,args):
        artists = self.get_topbands()
        irc.reply(', '.join(artists).encode('utf8','ignore'))

    def randband(self, irc, msg, args):
        """
        Returns a random band from the weekly top 
        artists chart of the code4lib last.fm group
        """
        artists = self.get_topbands()
        artist = artists[randint(0, len(artists)-1)]
        irc.reply(artist)

    def get_topbands(self):
        url = 'http://ws.audioscrobbler.com/1.0/group/code4lib/weeklyartistchart.xml'
        try:
            response = urlopen(url)
        except:
            irc.reply("d'oh can't get the weekly artist chart :(")
            return
        tree = ET.parse(response)
        root = tree.getroot()
        artists = []
        for track in root.findall('.//artist'):
            name = track.find('.//name')
            artists.append(name.text.strip())
        return artists

    def tagged (self,irc,msg,args):
        tag = quote(' '.join(args))
        url = "http://ws.audioscrobbler.com/1.0/tag/%s/topartists.xml" % tag 
        self.log.info(url)
        try:
            response = urlopen(url)
        except:
            irc.reply("no such tag or last.fm is on the fritz")
            return
            
        tree = ET.parse(response)
        root = tree.getroot()
        tags = []
        for artist in root.findall('.//artist'):
            tags.append("%s: %s%%" % (artist.attrib['name'],
                int(float(artist.attrib['count']))))
        irc.reply(' ; '.join(tags).encode('utf8','ignore'))

    def commontags(self,irc,msg,args):
      artists = ' '.join(args).split(':')
      tags = {}
      for artist in artists:
        url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml" % quote(artist.strip())
        try:
            response = urlopen(url)
        except:
            irc.reply("No tags found for %s" % ' '.join(args))
            return
        tree = ET.parse(response)
        root = tree.getroot()
        for tag in root.findall('.//tag'):
          name = tag.find(".//name").text
          if tags.has_key(name):
            tags[name] += 1
          else:
            tags[name] = 1

      common_tags = []
      for tag in tags:
        if tags[tag] == len(artists):
          common_tags.append(tag)
      irc.reply(' ; '.join(common_tags).encode('utf8','ignore'))

def shuffle(l):
   randomly_tagged_list = [(random(), x) for x in l]
   randomly_tagged_list.sort()
   return [x for (r, x) in randomly_tagged_list]

Class = AudioScrobbler 
