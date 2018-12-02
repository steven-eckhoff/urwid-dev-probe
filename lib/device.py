import configparser
from .bus import Bus
import os

class Register():
    
    def __init__(self, 
            addr, 
            page,
            precious,
            value = None):

        self.__addr = addr
        self.__page = page
        self.__precious = precious
    
    @property
    def addr(self):
        return self.__addr
    
    @property
    def page(self):
        return self.__page

    @property
    def precious(self):
        return self.__precious
    

class Device():

    def __init__(self, 
            dev_cfg_path,
            reg_cfg_path):

        if not os.path.isfile(dev_cfg_path):
            raise RuntimeError('{} does not exist'.format(dev_cfg_path))
        if not os.path.isfile(reg_cfg_path):
            raise RuntimeError('{} does not exist'.format(reg_cfg_path))
        
        self.__dev_cfg = configparser.ConfigParser()
        self.__dev_cfg.read(dev_cfg_path)
        self.__addr = self.__dev_cfg['DEFAULT']['addr']
        self.__page_reg = self.__dev_cfg['DEFAULT'].get('page_reg', None)

        self.__reg_cfg = configparser.ConfigParser()
        if reg_cfg_path:
            self.__reg_cfg.read(reg_cfg_path)

        self.__regs = dict()
        self.__reg_names = list()
        for reg in [self.__reg_cfg[s] for s in self.__reg_cfg.sections()]:
            name = reg.name
            addr = reg.get('addr')
            page = reg.get('page', None)
            precious = reg.getboolean('precious')
            self.__regs[name] = Register(addr, page, precious)
            self.__reg_names.append(name)
        self.bus = None

    @property
    def addr(self):
        return self.__addr

    @property
    def page_reg(self):
        return self.__page_reg

    def connect(self, bus):
        if isinstance(bus, Bus):
            self.bus = bus
        else:
            raise TypeError('Devices can only connect to Bus types')

    @property
    def reg_names(self):
        return self.__reg_names

    def reg_get(self, name):
        return self.__regs[name]

    def reg_read(self, name):
        if self.bus:
            reg = self.reg_get(name)
            return self.bus.read(self, reg)
        else:
            raise RuntimeError("Device not connected to bus")

    def reg_write(self, name, val):
        if self.bus:
            reg = self.reg_get(name)
            self.bus.write(self, reg, val)
        else:
            raise RuntimeError("Device not connected to bus")


