from ..amo.amo import AMO


class Entity:
	instance = None

	def __init__(self, config=None):
		self.config = config

	def __new__(cls, config=None):
		if not cls.instance:
			cls.instance = object.__new__(cls)
		return cls.instance

	def amo_init(self, config=None):
		if config:
			self.config = config
		return AMO(
			self.config[0],
			self.config[1],
			self.config[2],
			self.config[3],
			self.config[4],
			self.config[6],
			self.config[5]
		)
