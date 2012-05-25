
import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('StackEx', True)

StackEx = conf.registerPlugin('StackEx')

conf.registerGlobalValue(StackEx, 'waitPeriod', 
    registry.PositiveInteger(300, """Indicates how many seconds the bot will wait between retrieving questions"""))
