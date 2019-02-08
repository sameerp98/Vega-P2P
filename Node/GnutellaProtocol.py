from twisted.internet.protocol import Protocol, Factory

class GnutellaProtocol(Protocol):
	def dataReceived(self, data):
		#deserialize data
		#check descriptor type

class GnutellaFactory(Factory):
