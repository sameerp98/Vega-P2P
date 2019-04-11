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
import requests

from filetransfer import server
seenPingID = []
connections = []
createdPingID = []
myPongs = []
seenQueryID = []
myQuery = []
myQueryHit = []

class Gnutella (Protocol):
    # class Gnutella (basic.LineReceiver):
    def __init__(self):
        self.name = "Protocol Object"
        self.initiator = False
        #print("protocol init")

    def connectionMade(self):
        #print ("connection recevived")
        #print("appending connection ", self)
        #connections.append(self)
        peer = self.transport.getPeer()
        print("Connected to {0}:{1}".format(peer.host, peer.port))
        print("self address", self.transport.getHost().host, ":", self.transport.getHost().port)
        if self.initiator:
            self.transport.write("GNUTELLA CONNECT /0.4 \n\n".encode('utf-8'))
 
    def setInitializer(self):
        #print("idk")
        self.initiator = True

    def dataReceived(self, data):
        # stdout.write(data)
        #lines = data.split (";")
        # for line in lines:
        #	if len(line)>0:
        #print("data recieved", data)
        if data == "Gnutella OK \n\n".encode('utf-8'):
        	self.send_first_ping()
        elif data == "GNUTELLA CONNECT /0.4 \n\n".encode('utf-8'):
            self.handle_message(data)
        else:
            new_data = deserialize.deserialize(data)
            if new_data == None:
                return
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PONG:
                self.handle_pong(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.PING:
                print("\n\n got a ping from someone !\n\n")
                self.handle_ping(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.QUERY:
                self.handle_query(new_data)
            if new_data.descriptor_header.payload_descriptor == DescriptorHeader.QUERYHIT:
                self.handle_queryhit(new_data)

    def handle_message(self, data):
        #handle Gnutella CONNECT here
        #print("appending connection ", self)
        #connections.append(self)
        if self not in connections:
            #print("\n\n\n\nCONNECTION: \n\n\n\n", self)
            peer = self.transport.getPeer()
            #print("Connected to {0}:{1}".format(peer.host, peer.port))
            connections.append(self)
        self.transport.write("Gnutella OK \n\n".encode('utf-8'))
        return
    
    def send_first_ping(self):
        if self not in connections:
            #print("\n\n\n\nCONNECTION: \n\n\n\n", self)
            peer = self.transport.getPeer()
            print("Connected to {0}:{1}".format(peer.host, peer.port))
            connections.append(self)
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
        return

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
            print("this pong is too old, discarded")
            return
        for seenPing in seenPingID:
            if seenPing == pong.descriptor_header.descriptor_id:
                print("I know this ping so I will forward this pong")
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
        for q in myQuery:
            if queryhit.descriptor_header.descriptor_id == q:
                print("\nmy query hit !\n")
                print(queryhit)
                print("\n\n")
                myQueryHit.append(queryhit)
                #code for file transfer
                # for result in queryhit.result_set:
                #     print((result.file_name))
                resp = requests.get('http://'+queryhit.ip_address + ':' + '9020'\
                     + os.path.abspath(os.path.join('/files', queryhit.result_set[0].file_name)))
                file_name = queryhit.result_set[0].file_name[9:]
                print(file_name)
                print(os.path.join('/home/hp/Desktop/projects/VegaP2P/Vega-P2P/downloads/'\
                    , file_name))
                open(os.path.join('/home/hp/Desktop/projects/VegaP2P/Vega-P2P/downloads/'\
                    , file_name), 'wb')\
                    .write(resp.content)
                
                
                return 
        if queryhit.descriptor_header.ttl <= 0:
            print("query hit too old, discarded")
            return 

        for q in seenQueryID:
            if queryhit.descriptor_header.descriptor_id == q:
                print(" I have seen this query, so I will forward this queryhit")
                for cn in connections:
                    if cn != self:
                        cn.transport.write(queryhit.SerializeToString())
         

    def send_queryhit(self, query):
        queryhit = QueryHit()
        queryhit.descriptor_header.descriptor_id = query.descriptor_header.descriptor_id
        queryhit.descriptor_header.ttl = 7
        queryhit.descriptor_header.hops = 0
        queryhit.descriptor_header.payload_descriptor = DescriptorHeader.QUERYHIT
        file_name = query.search_criteria
        file_index = 0
        for path, dirs, files in os.walk("../files"):
            print("\nfiles --- \n",files)
            if path:
                current_path = path
            if files:
                for file in files:
                    print("\nfile = ", file)
                    if file_name in file:
                        new_file = QueryHit.ResultSet()
                        new_file.file_index = file_index
                        new_file.file_size = os.path.getsize(os.path.join(current_path, file))
                        new_file.file_name = os.path.join(current_path, file)
                        queryhit.result_set.extend([new_file])
                        file_index += 1
        if file_index == 0:
            print("\nfile not found -- no query hit generated\n")
            return
        queryhit.no_of_hits = file_index
        queryhit.ip_address = self.transport.getHost().host
        queryhit.speed = 23 #random
        queryhit.servent_identifier = query.descriptor_header.descriptor_id
        queryhit.port = self.transport.getHost().port
        queryhit.descriptor_header.payload_length = 4 + len(queryhit.result_set)
        print("\n\n----------query hit created ---------\n\n")
        print(queryhit)
        self.transport.write(queryhit.SerializeToString())
        """
        for cn in connections:
            cn.transport.write(queryhit.SerializeToString())
        """

class GnutellaFactory (Factory):
    def __init__(self, isInitializer=False):
        #print("factory init")
        self.initializer = False
        if isInitializer:
            self.initializer = True

    def buildProtocol(self, addr):
        prot = Gnutella()
        #print("protocol built")
        if self.initializer:
            prot.setInitializer()
        return prot

    def startedConnecting(self, connector):
        #print("Trying to connect")
        pass

    def clientConnectionFailed(self, transport, reason):
        #print("Client conneciton lost")
        pass

    def clientConnectionLost(self, transport, reason):
        reactor.stop()


def create_query(file_name):
    query = Query()
    query.descriptor_header.descriptor_id = str(uuid.uuid4())
    myQuery.append(query.descriptor_header.descriptor_id)
    query.descriptor_header.ttl = 7
    query.descriptor_header.hops = 0
    query.descriptor_header.payload_descriptor = DescriptorHeader.QUERY
    query.descriptor_header.payload_length = 4 + len(file_name)
    query.minimum_speed = 100
    query.search_criteria = file_name
    print("***\nquery created\n***")
    for cn in connections:
        cn.transport.write(query.SerializeToString())
            
def call_create_query(file_name):
    reactor.callFromThread(create_query, file_name)
	
    	
def get_user_input():
    while True:
        #print("\n--- inside the user input thread ---\n")
        file_name = input("enter file name :\n")
        call_create_query(file_name)

if __name__ == "__main__":
    # targetIp = sys.argv [1] #Enter IP then port
    #targetPort = sys.argv[2]
    #point = TCP4ClientEndpoint (reactor, targetIp,targetPort)
    #d = connectProtocol( point , Gnutella())
    #server = GnutellaFactory()
    #usedport= reactor.listenTCP(8007, server)
    # reactor.connectTCP("localhost",8000,GnutellaFactory(True))
    reactor.connectTCP("127.0.0.1", 8000, GnutellaFactory(True))
    reactor.callInThread(get_user_input)
    reactor.run()
