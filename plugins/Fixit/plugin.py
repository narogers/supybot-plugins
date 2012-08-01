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
               'create value for', 'facet', 're-index', 'relevance-rank',
               'monkeypatch', 'scrape', 'install', 'mashup', 'integrate',
               'snippet', 'wikify', 'network', 'proxy', 'toggle', 'reboot',
               'visualize', 'federate', 'curate', 'gamify', 'crowdsource',
               'scale up', 'cloud-host', 'progressively enhance', 
               'open-source'
      ]
      
      nouns = ['framework', 'html5', 'rubygem', 'shawarma', 'web app', 
               'nodefiddle', 'node.js', 'responsive design', 'SSID',
               'Apache', 'command line', 'supybot', 'repo', 'regexp',
               'model instance', 'heroku', 'EC2 instance', 'Islandora',
               'lambda function', 'RESTful JSON API', 'Solr', 'cloud', 
               'data', 'Drupal module', 'OAI-PMH', 'metadata', 'schema',
               'Blacklight', 'tweetybird', 'social media', 'backbone',
               'cross-universe compatibility', 'boilerstrap', 'html9',
               'beautifulsoup', 'failwhale', 'mashup', 'beans', 'cookies',
               'discovery layer', 'bits', 'architecture', 'github', 'zoia',
               'jquery', 'network', 'transistor', 'PDP-11', 'Fortran',
               'analytics', 'Z39.50', 'skunkworks', 'hadoop', 'persona',
               'web scale cloud ILS', 'scalability', 'singularity',
               'semantic web', 'triplestore', 'SFX', 'Fedora', 'Umlaut',
               'Ümläüt'
      ]
      
      verb = choice(verbs)
      object = choice(nouns)
      tool = choice(nouns)
      advice = "Just "+verb+" that "+object+" with your "+tool+"."
      irc.reply(advice, prefixNick=True)

Class = Fixit