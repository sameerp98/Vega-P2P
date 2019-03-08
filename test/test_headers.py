import unittest
import Node
import uuid
from twisted.internet.protocol import Protocol
from Node.descriptors_pb2 import DescriptorHeader, Ping, Pong, Query, QueryHit
import socket
import os

class TestDescriptionHeaders(unittest.TestCase):

	def test_ping(self):
		new_ping = Ping()
		new_ping.descriptor_header.ttl = 7
		self.assertEqual(new_ping.descriptor_header.ttl, 7)
		self.assertEqual(new_ping.descriptor_header.payload_descriptor, DescriptorHeader.PING)

	def test_pong(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 0))
		s.setblocking(False)
		local_ip_address = s.getsockname()[0] #returns ip and port
		new_pong = Pong()
		new_pong.ip_address = local_ip_address
		new_pong.descriptor_header.payload_descriptor = DescriptorHeader.PONG
		s.close()
		self.assertEqual(new_pong.descriptor_header.payload_descriptor, DescriptorHeader.PONG)
		self.assertEqual(new_pong.ip_address, local_ip_address)

	def test_query(self):
		new_query = Query()
		new_query.search_criteria = "xd"
		new_query.descriptor_header.payload_descriptor = DescriptorHeader.QUERY
		self.assertEqual(new_query.search_criteria, "xd")

	def test_query_hit(self):
		query = Query()
		query.descriptor_header.descriptor_id = str(uuid.uuid4())
		query.descriptor_header.ttl = 7
		query.descriptor_header.hops = 0
		query.descriptor_header.payload_descriptor = DescriptorHeader.QUERY
		query.descriptor_header.payload_length = 4
		query.minimum_speed = 100
		query.search_criteria = "xd"

		queryhit = QueryHit()
		queryhit.descriptor_header.descriptor_id = str(uuid.uuid4())
		queryhit.descriptor_header.ttl = 7
		queryhit.descriptor_header.hops = 0
		queryhit.descriptor_header.payload_descriptor = DescriptorHeader.QUERYHIT
		file_name = query.search_criteria
		result_set = []
		file_index = 0
		for path, dirs, files in os.walk("./files"):
			if path:
				current_path = path
			if files:
				for file in files:
					if file_name in file:
						new_file = queryhit.result_set.add()
						new_file.file_index = file_index
						new_file.file_size = os.path.getsize(os.path.join(current_path, file))
						new_file.file_name = os.path.join(current_path, file)
						print("a file found", new_file)
						file_index += 1
		queryhit.no_of_hits = file_index
		queryhit.ip_address = "192.168.23.24"
		queryhit.speed = 23
		queryhit.servent_identifier = query.descriptor_header.descriptor_id
		queryhit.port = 1111
		queryhit.descriptor_header.payload_length = 4 + len(queryhit.result_set)
		print(queryhit.SerializeToString())
		


