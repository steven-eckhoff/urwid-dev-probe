
from .pyBusPirateLite.I2Chigh import *
from .bus import Bus

class I2CPirateBus(Bus):
	
	def __init__(self, dev_path, speed):
		super().__init__()
		self.i2c = I2Chigh(dev_path, speed)
		self.i2c.BBmode()
		self.i2c.enter_I2C()
		#self.i2c.set_speed(I2CSpeed._50KHZ)
		self.i2c.set_speed(I2CSpeed._100KHZ)
		self.i2c.cfg_pins(I2CPins.POWER)

	def read(self, dev, reg):
		dev_addr = int(dev.addr, 16)
		reg_addr = int(reg.addr, 16)
		if reg.page:
			dev_page_reg = int(dev.page_reg, 16)
			reg_page = int(reg.page, 16)
			page_restore = self.i2c.get_byte(dev_addr, dev_page_reg)
			self.i2c.set_byte(dev_addr, dev_page_reg, reg_page)

		val = self.i2c.get_byte(dev_addr, reg_addr)

		if reg.page:
			self.i2c.set_byte(dev_addr, dev_page_reg, page_restore)

		return "0x{:02X}".format(val)

	def write(self, dev, reg, val):
		dev_addr = int(dev.addr, 16)
		reg_addr = int(reg.addr, 16)
		if reg.page:
			dev_page_reg = int(dev.page_reg, 16)
			reg_page = int(reg.page, 16)
			page_restore = self.i2c.get_byte(dev_addr, dev_page_reg)
			self.i2c.set_byte(dev_addr, dev_page_reg, reg_page)

		self.i2c.set_byte(dev_addr, reg_addr, int(val, 16))

		if reg.page:
			self.i2c.set_byte(dev_addr, dev_page_reg, page_restore)
