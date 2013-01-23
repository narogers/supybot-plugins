from supybot.commands import *
import supybot.callbacks as callbacks

import sys
import urllib
from lxml.etree import fromstring

app_id = '62VUEW-H6XTUTU32R'

class Wolfram(callbacks.Privmsg):

    def alpha(self, irc, msg, args, verbose, question):
        """
        Usage: @alpha [-v|--verbose] question
        Ask Mr. Wolfram a question, get an "answer"...maybe? It uses the
        Wolfram Alpha API.
        <http://products.wolframalpha.com/docs/WolframAlpha-API-Reference.pdf>

        """
        u = "http://api.wolframalpha.com/v2/query?"
        q = urllib.urlencode({'input': question, 'appid': app_id})
        xml = urllib.urlopen(u + q).read()
        tree = fromstring(xml)
        try:
            assert tree.xpath('/queryresult')[0].attrib['success'] == 'true'
            result = tree.xpath('//subpod[@primary="true"]/plaintext/text()')[0]
            irc.reply("Answer: %s" % result.encode('utf-8'))
            if verbose:
                for pod in tree.xpath('//pod[not(@primary)]'):
                    title = pod.attrib['title']
                    for plaintext in pod.findall('.//plaintext'):
                        if plaintext.text:
                            irc.reply(("%s: %s" % (title, plaintext.text)).encode('utf-8'))
        except AssertionError:
            irc.error("huh, I dunno, I'm still a baby AI. Wait till the singularity I guess?")
        except Exception, e:
            irc.error("huh, I dunno, Something went kablooie.")
            import traceback
            traceback.print_stack()
            traceback.print_exc()

    alpha = wrap(alpha, [optional(("literal", ("--verbose","-v"))), 'text'])
#    alpha = wrap(alpha, ['text'])


Class = Wolfram
