import unittest
<<<<<<< HEAD
from Node import gnutellaSender
from Node import gnutellaServer
=======
from Node import gnutellaSender as Sender
from Node import gnutellaServer as Server
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor
>>>>>>> cd253c5ff893bf09a2b2d67c5a58f6aa1385f7c0

class TestProtocol(unittest.TestCase):

	def test_connection(self):
<<<<<<< HEAD
		server = gnutellaServer.GnutellaFactory()
    	usedport = reactor.listenTCP(8000, server)
		reactor.connectTCP("127.0.0.1", 8000, GnutellaFactory(True))
    	reactor.run()
=======
		used_port = []
		try:
			new_server = Server.GnutellaFactory()
			for i in range(0, 2):
				used_port.append(reactor.listenTCP(8000 + i, new_server))
			for i in range(0, 2):
				reactor.connectTCP("127.0.0.1", 8000 + i, Sender.GnutellaFactory(True))
			reactor.run()
		except Exception as e:
			print(e)
>>>>>>> cd253c5ff893bf09a2b2d67c5a58f6aa1385f7c0


	def test_scan(self):
		self.assertEqual(True, True)

	def test_ping(self):
		self.assertEqual(True, True)

	def test_query(self):
		self.assertEqual(True, True)
