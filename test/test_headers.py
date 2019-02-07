import unittest
import Node
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
		self.assertEqual(new_pong.descriptor_header.payload_descriptor, DescriptorHeader.PONG)
		self.assertEqual(new_pong.ip_address, local_ip_address)

	def test_query(self):
		new_query = Query()
		new_query.search_criteria = "xd"
		self.assertEqual(new_query.search_criteria, "xd")

	def test_query_hit(self):
		new_query_hit = QueryHit()
		result_set = []
		file_index = 0
		for path, dirs, files in os.walk("./files"):
			if path:
				current_path = path
			if files:
				for file in files:
					new_file = new_query_hit.result_set.add()
					new_file.file_index = file_index
					new_file.file_size = os.path.getsize(os.path.join(current_path, file))
					new_file.file_name = os.path.join(current_path, file)
					file_index += 1
		


