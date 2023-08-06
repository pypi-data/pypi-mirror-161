import logging

log = logging.getLogger()

class WriterCSV():
    def __init__(self,filename:str):
        log.debug("Init WriterCSV")
        self.__filename = filename
    def open(self):
        log.debug("Opening file for write csv data")
        self.__file = open(self.__filename,"w")
    def writeLine(self,line:str):
        self.__file.write("{0}{1}".format(line,'\n'))
    def close(self):
        log.debug("Closing file for write")
        self.__file.close()
    def __del__(self):
        log.debug("Del WriterCSV")
        self.close()