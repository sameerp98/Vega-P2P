from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.protocols import basic
import deserialize
from descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
import uuid
connections = []


class Gnutella (Protocol):
    # class Gnutella (basic.LineReceiver):
    def __init__(self):
        self.name = "Protocol Object"
        print("protocol init")
        #self.initiator= False
        # if isInitiator:
        #    self.initiator= True

    def connectionMade(self):
        print ("connection recevived")
        
        # add client here

    def setInitializer(self):
        print("self init")
        self.initiator = True

    def dataReceived(self, data):
        # stdout.write(data)
        print("Server received data", data)
        if data == "GNUTELLA CONNECT /0.4 \n\n":
            self.handle_message(data)
        else:
            new_data = deserialize.deserialize(data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PING:
                self.handle_ping(new_data)

    def handle_message(self, data):
        print("appending connection ", self)
        connections.append(self)
        peer = self.transport.getPeer()
        print("Connected to {0}:{1}".format(peer.host, peer.port))
        self.transport.write("Gnutella OK \n\n")
        """peer = self.transport.getPeer()
        # if (type(data)== type(Ping)):
        print("sending pong to {0}".format(peer.host))
        # construct ping from incoming data
        self.handle_ping(data)  # insert ping object here"""

    def send_ping(self, ping):
        # if ping.ttl < 0:#when receiving ping
        #    return
        # if ping.payload_descriptor:
        #    print ("Forwarding Ping")
        #    p = ping
        # serialize p object
        # else:
        #    p = ping ("Dummy Payload")
                        # serialize p object
        if ping.descriptor_header.ttl <= 0:
            return
        p = ping.SerializeToString()
        print("Sending ping")
        for cn in connections:
            cn.transport.write(p)  # send p object here

    def handle_ping(self, ping):
        print("handling ping")
        ping.descriptor_header.ttl -= 1
        self.send_ping(ping)
        self.send_pong(ping)

    def send_pong(self, ping):
        pong = Pong()
        pong.descriptor_header.descriptor_id = str(uuid.uuid4())
        pong.descriptor_header.ttl = 7
        pong.descriptor_header.hops = 4
        pong.descriptor_header.payload_descriptor = DescriptorHeader.PONG
        pong.descriptor_header.payload_length = 14
        pong.port = self.transport.getPeer().port
        pong.ip_address = self.transport.getPeer().host
        pong.no_of_files_shared = 5
        pong.no_of_kb_shared = 1000
        print("pong created")
        p = pong.SerializeToString()
        for cn in connections:
            cn.transport.write(p)  # send p object here


class GnutellaFactory (Factory):
    def __init__(self, isInitializer=False):
        print("factory init")
        self.initializer = False
        if isInitializer:
            self.initializer = True

    def buildProtocol(self, addr):
        print("protocol built")
        prot = Gnutella()
        if self.initializer:
            prot.setInitializer()
        return prot

    def startedConnecting(self, connector):
        print("Trying to connect")

    def clientConnectionFailed(self, transport, reason):
        print("Client conneciton lost")


if __name__ == "__main__":
    server = GnutellaFactory()
    usedport = reactor.listenTCP(8000, server)
    reactor.run()
