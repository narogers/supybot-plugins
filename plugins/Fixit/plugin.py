from supybot.commands import *
from random import choice
import supybot.callbacks as callbacks

class Fixit(callbacks.Plugin):

    def fixit(self, irc, msg, args):
      """
      Get advice for solving your intractable tech problems.
      """
      
      verbs = ['attackclone', 'bootstrap', 'tweetybird', 'architect', 
               'merge', 'compile', 'boilerstrap', 'git push', 'fork',
               'configure', 'hash', 'salt', 'commit', 'echo', 'version',
               'create value for', 'facet', 're-index', 'relevance-rank'
      ]
      
      nouns = ['framework', 'html5', 'rubygem', 'shawarma', 'web app', 
               'nodefiddle', 'node.js', 'responsive design', 'SSID',
               'Apache', 'command line', 'supybot', 'repo', 'regexp',
               'model instance', 'heroku', 'EC2 instance', 'Islandora',
               'lambda function', 'RESTful JSON API', 'Solr', 'cloud', 
               'data', 'Drupal module', 'OAI-PMH', 'metadata', 'schema',
               'Blacklight', 'tweetybird', 'social media', 'backbone',
               'cross-universe compatibility', 'boilerstrap', 'html9'
      ]
      
      verb = choice(verbs)
      object = choice(nouns)
      tool = choice(nouns)
      advice = "Just "+verb+" that "+object+" with your "+tool+"."
      irc.reply(advice, prefixNick=True)

Class = Fixit