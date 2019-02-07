import unittest
import Node
from twisted.internet.protocol import Protocol
from Node.Headers import Ping, Pong, Query, QueryHit
import socket

class TestDescriptionHeaders(unittest.TestCase):

	def test_ping(self):
		new_ping = Ping()
		self.assertEqual(new_ping.ttl, 7)
		self.assertEqual(new_ping.hops, 0)
		self.assertEqual(new_ping.payload_descriptor, "ping")

	def test_pong(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 0))
		s.setblocking(False)
		local_ip_address = s.getsockname()[0] #returns ip and port
		new_pong = Pong()
		self.assertEqual(new_pong.payload_descriptor, "pong")
		self.assertEqual(Pong.ip, local_ip_address)

	def test_query(self):
		new_query = Query(search_criteria = "xd")
		self.assertEqual(Query.search_criteria, "xd")
'''
	def test_query_hit(self):
		new_query_hit = QueryHit(hits=10, speed=4, result_set=)
'''




