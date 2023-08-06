from PyQt6 import QtCore, QtGui, QtWidgets
from ammeter_fpn_4_24.model import Model   
import logging

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)

class EntryPoint:    
    def run(self):
        import sys
        app = QtWidgets.QApplication(sys.argv)
        model = Model(app)
        sys.exit(app.exec())

def startup():
    entryPoint = EntryPoint()
    log = logging.getLogger()
    #log.setLevel(logging.DEBUG)
    entryPoint.run()
    
if __name__ == "__main__":
    startup()