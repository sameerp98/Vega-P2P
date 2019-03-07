import sys
sys.path.append('../')
from Node.descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
import uuid
def deserialize(header):
	
	if len(header) < 48:
		#GNUTELLA OKAY
		return header	
	#print("\n\n", ord(header[45:46]), "type = ", len(header[45:46]))
	if ord(header[45:46]) == DescriptorHeader.PING:
		its_ping = Ping()
		its_ping.ParseFromString(header)
		return its_ping

	if ord(header[45:46]) == DescriptorHeader.PONG:
		its_pong = Pong()
		its_pong.ParseFromString(header)
		return its_pong

	if ord(header[45:46]) == DescriptorHeader.QUERY:
		its_query = Query()
		its_query.ParseFromString(header)
		return its_query

	if ord(header[45:46]) == DescriptorHeader.QUERYHIT:
		its_query_hit = QueryHit()
		its_query_hit.ParseFromString(header)
		return its_query_hit

