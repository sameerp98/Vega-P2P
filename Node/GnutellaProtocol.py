from twisted.internet.protocol import Protocol, Factory

class GnutellaProtocol(Protocol):
	def __init__(self):
		self.status = "incomplete"

class GnutellaFactory(Factory):
	def __init__(self):
		self.status = "incomplete"