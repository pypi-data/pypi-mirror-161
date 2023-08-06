#Third party module
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import numpy as np
#Python module
import logging

log = logging.getLogger()

def testConnection(host,port):
    client = ModbusTcpClient(host, port=port)
    client.connect()
    client.close()


def validator(instance):
    if not instance.isError():
        '''.isError() implemented in pymodbus 1.4.0 and above.'''
        decoder = BinaryPayloadDecoder.fromRegisters(
            instance.registers,
            byteorder=Endian.Big, wordorder=Endian.Little
        )  
        res = decoder.decode_16bit_int()
        print (res)
        return float('{0:.2f}'.format(res))

    else:
        # Error handling.
        print("The register does not exist, Try again.")
        return None

class Handler():
    def __init__(self,host:str,port:int,id:int):
        self.__client = ModbusTcpClient(host, method="rtu", port=port, framer=ModbusRtuFramer,timeout=3)#,skip_encode = True)
        self.__id = id
        self.status = False

    def __del__(self):
        if self.status:
            self.disconnect()

    def connect(self):
        log.debug("modbus connecting")
        self.status = True
        return self.__client.connect()

    def disconnect(self):
        log.debug("modbus disconnecting")
        self.status = False
        self.__client.close()
    
    def readRegisters(self, startAdrress:int, count:int=1):
        log.debug("Read modbus registers")
        response = self.__client.read_holding_registers(startAdrress, count, unit=self.__id)
        log.debug(response)
        res = self.__checkArrayValueByNegative(response.registers)
        return res
    def readRegister32Bit(self, adrress:int):
        log.debug("Read modbus register 32 bit")
        response = self.__client.read_holding_registers(adrress, 2, unit=self.__id)
        log.debug(response)
        decoder = BinaryPayloadDecoder.fromRegisters(
            response.registers,
            byteorder=Endian.Big, wordorder=Endian.Little
        )  
        return decoder.decode_32bit_int()
    def writeRegister(self,startAddress:int, data:int):
        log.debug("Write modbus register")
        response = self.__client.write_register(startAddress, data, unit=self.__id)
        log.debug(response)
        return response

    def __checkArrayValueByNegative(self,array):
        resultArray = np.zeros(shape=np.size(array),dtype=int)
        for i in range(np.size(array)):
            resultArray[i] = array[i] if array[i] < 2**15 else array[i] -2**16
        return resultArray