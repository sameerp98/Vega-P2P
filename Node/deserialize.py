from descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
import uuid
def deserialize(header):
	if ord(header[45:46]) == DescriptorHeader.PING:
		its_ping = Ping()
		#print(header)
		its_ping.ParseFromString(header)
		return its_ping

	if ord(header[45:46]) == DescriptorHeader.PONG:
		its_pong = Pong()
		#print(header)
		its_pong.ParseFromString(header)
		return its_pong

	if ord(header[45:46]) == DescriptorHeader.QUERY:
		its_query = Query()
		#print(header)
		its_query.ParseFromString(header)
		return its_query

	if ord(header[45:46]) == DescriptorHeader.QUERYHIT:
		its_query_hit = QueryHit()
		#print(header)
		its_query_hit.ParseFromString(header)
		return its_query_hit

if __name__ == '__main__':
	new_ping = Ping()
	new_ping.descriptor_header.ttl = 7
	new_ping.descriptor_header.descriptor_id = str(uuid.uuid4())
	new_ping.descriptor_header.hops = 4
	new_ping.descriptor_header.payload_descriptor = DescriptorHeader.PING
	new_ping.descriptor_header.payload_length = 5
	print(deserialize(new_ping.SerializeToString()))
