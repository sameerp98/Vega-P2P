import unittest
from Node import gnutellaSender
from Node import gnutellaServer

class TestProtocol(unittest.TestCase):

	def test_connection(self):
		server = gnutellaServer.GnutellaFactory()
    	usedport = reactor.listenTCP(8000, server)
		reactor.connectTCP("127.0.0.1", 8000, GnutellaFactory(True))
    	reactor.run()


	def test_scan(self):
		self.assertEqual(True, False)

	def test_ping(self):
		self.assertEqual(True, False)

	def test_query(self):
		self.assertEqual(True, False)
