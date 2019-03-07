import sys
sys.path.append('../')
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor
import Node.deserialize as deserialize
import uuid
from Node.descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
#from twisted.protocols import basic
import sys
import os
seenPingID = []
connections = []
createdPingID = []
myPongs = []


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
            self.transport.write("GNUTELLA CONNECT /0.4 \n\n".encode('utf-8'))
 
    def setInitializer(self):
        print("idk")
        self.initiator = True

    def dataReceived(self, data):
        # stdout.write(data)
        #lines = data.split (";")
        # for line in lines:
        #	if len(line)>0:
        print("data recieved", data)
        if data == "Gnutella OK \n\n".encode('utf-8'):
        	self.send_first_ping()
        else:
            new_data = deserialize.deserialize(data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PONG:
                self.handle_pong(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PING:
                print("\n\n got a ping from someone !\n\n")
                self.handle_ping(new_data)

    def handle_message(self, data):
        #handle gnutella connect and gnutella ok here
        peer = self.transport.getPeer()
        print("sending ping to {0}".format(peer.host))
        self.send_first_ping()

    def send_first_ping(self):
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
                print("pong for me ! appending")
                myPongs.append(pong)
                return
        print("not my pong")
        pong.descriptor_header.ttl -= 1
        if pong.descriptor_header.ttl <= 0:
            print("this pong too old, discarded")
            return
        for seenPing in seenPingID:
            if seenPing == pong.descriptor_header.descriptor_id:
                print("oh I know this ping so I will forward this pong")
                p = pong.SerializeToString()
                for cn in connections:
                    cn.transport.write(p)
                    return 
        print("I guess I dont know the pong ... discarded")

    
    def handle_ping(self, ping):
        print("handling ping")
        for seenPing in seenPingID:
            if seenPing == ping.descriptor_header.descriptor_id:
                print("already recieved this ping, discarded")
                return
        seenPingID.append(ping.descriptor_header.descriptor_id)
        ping.descriptor_header.ttl -= 1
        ping.descriptor_header.hops += 1
        self.send_ping(ping)
        self.send_pong(ping)

    def send_ping(self, ping):
        if ping.descriptor_header.ttl <= 0:
            return
        p = ping.SerializeToString()
        print("Sending ping")
        for cn in connections:
            if cn != self:
                cn.transport.write(p)  
    
    def send_pong(self, ping):
        pong = Pong()
        pong.descriptor_header.descriptor_id = ping.descriptor_header.descriptor_id
        pong.descriptor_header.ttl = 7
        pong.descriptor_header.hops = 0
        pong.descriptor_header.payload_descriptor = DescriptorHeader.PONG
        pong.descriptor_header.payload_length = 14
        pong.port = self.transport.getHost().port
        pong.ip_address = self.transport.getHost().host
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
