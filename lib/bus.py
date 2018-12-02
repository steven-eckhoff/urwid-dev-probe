
from abc import ABCMeta, abstractmethod

class Bus(metaclass=ABCMeta):
	
	@abstractmethod
	def read(self, dev, reg):
		pass

	@abstractmethod
	def write(self, dev, reg, val):
		pass
