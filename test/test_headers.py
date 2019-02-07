import unittest
import Node
from Node.Headers import Ping, Pong, Query, QueryHit

class TestDescriptionHeaders(unittest.TestCase):

	def test_ping(self):
		new_ping = Ping.Ping(payload_descriptor = "payload")
		self.assertEqual(new_ping.ttl, 7)
		self.assertEqual(new_ping.hops, 0)
		self.assertEqual(new_ping.payload_descriptor, "payload")


