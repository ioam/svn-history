## rename to buildbot.tac before use

from twisted.application import service
from buildbot.slave.bot import BuildSlave

basedir = r'/home/ceball/buildbot/buildslave/x86_ubuntu7.04'
host = 'localhost'
port = 9989
slavename = 'x86_ubuntu7.04'
passwd = 'PWD'
keepalive = 600
usepty = 1
umask = None

application = service.Application('buildslave')
s = BuildSlave(host, port, slavename, passwd, basedir, keepalive, usepty,
               umask=umask)
s.setServiceParent(application)

