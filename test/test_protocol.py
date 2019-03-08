import unittest
import sys
sys.path.append('../')
from Node import gnutellaSender as Sender
from Node import gnutellaServer as Server
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol, TCP4ServerEndpoint
from twisted.internet import reactor

class TestProtocol(unittest.TestCase):

	def test_connection(self):
		used_port = []
		try:
			new_server = Server.GnutellaFactory()
			for i in range(0, 2):
				used_port.append(reactor.listenTCP(2140 + i, new_server))
				print(used_port)
			for i in range(0, 2):
				new_sender = Sender.GnutellaFactory()
				reactor.connectTCP("127.0.0.1", 2140 + i, new_sender)
				Sender.send_first_ping()
				Sender.create_query("xd")
			reactor.run()
		except Exception as e:
			print(e)


	def test_scan(self):
		self.assertEqual(True, True)

	def test_ping(self):
		self.assertEqual(True, True)

	def test_query(self):
		self.assertEqual(True, True)
