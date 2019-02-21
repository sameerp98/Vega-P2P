from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor
import deserialize
import uuid
from descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
#from twisted.protocols import basic
import sys
connections = []
createdPingID = []

class Gnutella (Protocol):
    # class Gnutella (basic.LineReceiver):
    def __init__(self):
        self.name = "Protocol Object"
        print("protocol init")

    def connectionMade(self):
        #print ("connection recevived")
        print("appending connection ", self)
        connections.append(self)
        peer = self.transport.getPeer()
        print("Connected to {0}:{1}".format(peer.host, peer.port))
        print("self address", self.transport.getHost().host, ":", self.transport.getHost().port)
        if self.initiator:
            self.transport.write("GNUTELLA CONNECT /0.4 \n\n")

    def setInitializer(self):
        print("idk")
        self.initiator = True

    def dataReceived(self, data):
        # stdout.write(data)
        #lines = data.split (";")
        # for line in lines:
        #	if len(line)>0:
        print("data recieved", data)
        if data == "Gnutella OK \n\n":
        	self.send_ping()
        else:
            new_data = deserialize.deserialize(data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PONG:
                self.handle_pong(new_data)

    def handle_message(self, data):
        #handle gnutella connect and gnutella ok here
        peer = self.transport.getPeer()
        print("sending ping to {0}".format(peer.host))
        self.send_ping()

    def send_ping(self):
        # if ping.ttl < 7:
        #	return
        # if ping.payload_descriptor:
        #	print ("Forwarding Ping")
        # else:
        #	p = ping ("Dummy Payload")
            # serialize
        ping = Ping()
        ping.descriptor_header.ttl = 7
        ping.descriptor_header.descriptor_id = str(uuid.uuid4())
        ping.descriptor_header.hops = 0
        ping.descriptor_header.payload_descriptor = DescriptorHeader.PING
        ping.descriptor_header.payload_length = 0
        createdPingID.append(ping.descriptor_header.descriptor_id)
        print("Ping is being sent")
        for cn in connections:
            cn.transport.write(ping.SerializeToString())
    
    def handle_pong(self, pong):
        #if the pong id matched created ping id, save it somehow
        #else discard it
        print("pong recieved ", pong)
        for id in createdPingID:
            if id == pong.descriptor_header.descriptor_id:
                print("pong will be appended")
                return
        print("not my pong, discarded")

class GnutellaFactory (Factory):
    def __init__(self, isInitializer=False):
        print("factory init")
        self.initializer = False
        if isInitializer:
            self.initializer = True

    def buildProtocol(self, addr):
        prot = Gnutella()
        print("protocol built")
        if self.initializer:
            prot.setInitializer()
        return prot

    def startedConnecting(self, connector):
        print("Trying to connect")

    def clientConnectionFailed(self, transport, reason):
        print("Client conneciton lost")

    def clientConnectionLost(self, transport, reason):
        reactor.stop()


if __name__ == "__main__":
    # targetIp = sys.argv [1] #Enter IP then port
    #targetPort = sys.argv[2]
    #point = TCP4ClientEndpoint (reactor, targetIp,targetPort)
    #d = connectProtocol( point , Gnutella())
    #server = GnutellaFactory()
    #usedport= reactor.listenTCP(8007, server)
    # reactor.connectTCP("localhost",8000,GnutellaFactory(True))
    reactor.connectTCP("127.0.0.1", 8000, GnutellaFactory(True))
    reactor.run()
