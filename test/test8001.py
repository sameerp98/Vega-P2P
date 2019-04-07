import sys
sys.path.append('../')
from Node import gnutellaSender as Sender

from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor



def start_gnutella(port, ip):
    server = Sender.GnutellaFactory()
    reactor.listenTCP(8000+port, server)
    gnutella_connect(port, ip)
    reactor.callInThread(Sender.get_user_input)
    reactor.run()

def gnutella_connect(port, ip):
    for i in range(0,100):
        if i!=port:
            reactor.connectTCP("127.0.0.1", 8000+i, Sender.GnutellaFactory(True))

if __name__ == "__main__":
    start_gnutella(1, 100)
    get_user_input()