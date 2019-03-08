import sys
sys.path.append('../')
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.protocols import basic
import Node.deserialize as deserialize
from Node.descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
import uuid
connections = []
seenPingID = []
seenQueryID = []



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
       # print("\ntest 1\n\n", DescriptorHeader.PONG," ---- ", type(DescriptorHeader.PONG), "\n\n")
        if data == "GNUTELLA CONNECT /0.4 \n\n".encode('utf-8'):
            self.handle_message(data)
        else:
            new_data = deserialize.deserialize(data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PING:
                self.handle_ping(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PONG:
                self.handle_pong(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.QUERY:
                self.handle_query(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.QUERYHIT:
                self.handle_queryhit(new_data)

    def handle_message(self, data):
        # handle the gnutella connect and gnutella ok here
        print("appending connection ", self)
        connections.append(self)
        peer = self.transport.getPeer()
        print("Connected to {0}:{1}".format(peer.host, peer.port))
        self.transport.write("Gnutella OK \n\n".encode('utf-8'))

    def send_ping(self, ping):
        #send ping to all connections except self 
        #save the ping id for later use 
        # do we remove the ping id based on time ?  
        if ping.descriptor_header.ttl <= 0:
            return
        p = ping.SerializeToString()
        print("Sending ping")
        print(self)
        for cn in connections:
            print("\n\n********************* connection *******************\n\n")
            print(cn)
            if cn != self:
                print("yep")
                cn.transport.write(p)  
        return

    def handle_ping(self, ping):
        # append the ping id to seen array 
        # add some time logic to updating the array 
        # create and send the pong for ping
        # forward the ping to other nodes
        print("\n\n-----handling ping-----\n\n")
        print(ping)
        for seenPing in seenPingID:
            if seenPing == ping.descriptor_header.descriptor_id:
                print("already recieved this ping, discarded")
                return
        seenPingID.append(ping.descriptor_header.descriptor_id)
        ping.descriptor_header.ttl -= 1
        ping.descriptor_header.hops += 1
        self.send_ping(ping)
        self.send_pong(ping)

    def send_pong(self, ping):
        # this method creates first pong
        # number of files and size to be calculated and added later
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
        return 
    
    def handle_pong(self, pong):
        print("pong recieved ", pong)
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
    
    def handle_query(self, query):
        print("\n---- recieved a query ----\n", query)
        for seenQuery in seenQueryID:
            if query.descriptor_header.descriptor_id == seenQuery:
                print("already recieved this query, discarded")
                return
        seenQueryID.append(query.descriptor_header.descriptor_id)
        if query.descriptor_header.ttl <= 0:
            print("query too old, discarded")
            return 
        query.descriptor_header.ttl -= 1
        for cn in connections:
            if cn != self:
                cn.transport.write(query.SerializeToString())
        self.send_queryhit(query)
    
    def handle_queryhit(self, queryhit):
        print("\n\n------ received a query hit ! ------\n\n")
        if queryhit.descriptor_header.ttl <= 0:
            print("query hit too old, discarded")
            return 

        for q in seenQueryID:
            if queryhit.descriptor_header.id == q:
                print(" I have seen this query, so I will forward this queryhit")
                for cn in connections:
                    if cn != self:
                        cn.transport.write(queryhit.SerializeToString())

    def send_queryhit(self, query):
        queryhit = QueryHit()
        queryhit.descriptor_header.id = str(uuid.uuid4())
        query.descriptor_header.ttl = 7
        query.descriptor_header.hop = 0
        query.descriptor_header.payload_descriptor = DescriptorHeader.QUERYHIT
        file_name = query.search_criteria
        result_set = []
        file_index = 0
        for path, dirs, files in os.walk("./files"):
            if path:
                current_path = path
            if files:
                for file in files:
                    if file in file_name:
                        new_file = query_hit.result_set.add()
                        new_file.file_index = file_index
                        new_file.file_size = os.path.getsize(os.path.join(current_path, file))
                        new_file.file_name = os.path.join(current_path, file)
                        file_index += 1
        if file_index == 0:
            return
        queryhit.no_of_hits = file_index
        queryhit.ip_address = self.transport.getHost().host
        queryhit.speed = 23 #random
        queryhit.servent_identifier = query.descriptor_header.descriptor_id
        queryhit.port = self.transport.getHost().port
        queryhit.descriptor_header.payload_length = 4 + len(queryhit.result_set)
        for cn in connections:
            if cn != self:
                cn.transport.write(queryhit)

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
