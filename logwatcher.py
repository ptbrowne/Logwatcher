from twisted.internet import inotify, reactor
from twisted.python import filepath
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
from datetime import datetime
import json
import pprint

class FileWatcher(object) :
    """
    Enables you to watch a file for change.
    Fires toNotify.lineReceived for each line that is
    added to the watched file.
    """
    def __init__(self, fp, toNotify) :
        notifier = inotify.INotify()
        notifier.startReading()
        notifier.watch(filepath.FilePath(fp), callbacks=[self.eventReceived])
        
        self.fp = fp
        self.f = open(fp, "r")
        self.f.seek(0,2)
        self.toNotify = toNotify
    
    def eventReceived(self, _Watch, filepath, mask):
        print "event %s on %s" % (
            ', '.join(inotify.humanReadableMask(mask)), filepath)
        for line in self.f.readlines():
            self.lineReceived(line)

    def watch(self, fp):
        notifier.watch(filepath.FilePath(fp), callbacks=[self.eventReceived])

    def ignore(self, fp):
        notifier.ignore(filepath.FilePath(fp))

    def lineReceived(self, line):
        self.toNotify.lineReceived(line.strip(), self.fp)

class FileWatcherProtocol(WebSocketServerProtocol):    
    def onOpen(self):
      self.factory.register(self)

    def onClose(self, _, code, reason):
      self.factory.unregister(self)
       
    def onMessage(self, msg, binary):
        request = json.loads(msg)
        print request
        if "watch" in request:
            self.factory.watch(self, request["watch"])
        elif "unwatch" in request:
            self.factory.unwatch(self, request["unwatch"])
        else:
            print "bad request"

class FileWatcherServerFactory(WebSocketServerFactory):
 
    protocol = FileWatcherProtocol
 
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        self.watchers = {}
        self.clients_watchers = []
        self.tickcount = 0
        #self.tick()

    def tick(self):
        self.tickcount += 1
        self.broadcast(json.dumps({"type" : "debug", "msg" : "tick %d" % self.tickcount}))
        reactor.callLater(15, self.tick)

    def register(self, client):
        if not client in self.clients:
            print "registered client " + client.peerstr
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print "unregistered client " + client.peerstr
            self.clients.remove(client)
            self.clients_watchers = filter(lambda c : c[0] != client.peerstr, self.clients_watchers)
             
    def nb_clients(self, fp):
        return sum(1 for (_, fp2) in self.clients_watchers if fp == fp2)
        
    def watch(self, client, fp):
        if fp not in self.watchers :
            watcher = FileWatcher(fp, self)
            self.watchers[fp] = {"nb_client" : 0}
        if (client.peerstr, fp) not in self.clients_watchers:
            self.clients_watchers.append( (client.peerstr, fp) )
            print "%s started to follow %s. %s has now %i followers" % (client.peerstr, fp, fp, self.nb_clients(fp))
            
    def unwatch(self, client, fp):
        if (client.peerstr, fp) in self.clients_watchers:
            self.clients_watchers.remove( (client.peerstr, fp) )
            print "%s finished to follow %s. %s has now %i followers" % (client.peerstr, fp, fp, self.nb_clients(fp))
             
    def lineReceived(self, line, fp):
        print "file %s : %s" % (fp, line) 
        for c in self.clients:
             if (c.peerstr, fp) in self.clients_watchers:
                c.sendMessage(json.dumps({"type" : "msg", "file" : fp, "line" : line}))
                print "send to " + c.peerstr
 
    def broadcast(self, msg):
        for c in self.clients:
                c.sendMessage(msg)
                print "send to " + c.peerstr  

if __name__ == '__main__':
    factory = FileWatcherServerFactory("ws://localhost:9000")
    listenWS(factory)
    reactor.run()
