import json
import time
import gzip
import urllib2

from StringIO import StringIO

from supybot.commands import *
import supybot.callbacks as callbacks

class StackEx(callbacks.Plugin):
    """silly stuff to do with http://libraries.stackexchange.com/
    """
    threaded = True

    def __init__(self, irc):
        self.__parent = super(StackEx, self)
        self.__parent.__init__(irc)
        # when starting up fetch any questions in the last two hours
        self.last_request = int(time.time()) - (2 * 60 * 60)

    def __call__(self, irc, msg):
        self.__parent.__call__(irc, msg)
        now = time.time()
        wait = self.registryValue('waitPeriod')
        if now - self.last_request > wait:
            self.last_request = int(now)
            irc = callbacks.SimpleProxy(irc, msg)
            questions = get_questions(last_request)
            if len(questions) > 0:
                n = ["%s <%s>" % (q.title, q.url) for q in questions]
                irc.reply('new library questions: ' + ' ; '.join(n), to='#code4lib', prefixNick=False)

    def last_question(self, irc, msg, args):
        """returns the last libraries stack exchange question
        """
        t = int(time.time())
        q = get_questions(0)[0]
        irc.reply("%s <%s>" % (q['title'], q['url']))

    last_question = wrap(last_question)

def get_questions(from_date):
    new_questions = []
    # all stack exchange api calls return gzipped content
    # kinda sucky that urllib2 doesn't hande gzip :(
    url = "http://api.stackexchange.com/2.0/questions?order=desc&sort=creation&site=libraries.stackexchange.com&fromdate=%s" % from_date
    response = urllib2.urlopen(url)
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    questions = json.loads(data)
    for question in questions['items']:
        new_questions.append({'title': question['title'], 'url': question['link']})

    return new_questions

Class = StackEx

if __name__ == "__main__":
    now = time.time()
    then = now - (2 * 60 * 60) # an hour ago
    for q in get_questions(int(then)):
        print "%s <%s>" % (q['title'], q['url'])
