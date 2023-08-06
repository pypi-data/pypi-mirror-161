#Project module
from ammeter_fpn_4_24.ui import uic as uicFile
from ammeter_fpn_4_24 import modbusRTUOverTCP, backWorking
#Third party module
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
import numpy as np
#Python module
from pkg_resources import resource_listdir,resource_filename
import logging
from enum import Enum


log = logging.getLogger()


class DialogConfig(QtWidgets.QDialog):
    def __init__(self,parent=None,host:str="192.168.100.140",port=4001,id=100):
        super().__init__(parent=parent)
        str = resource_filename(uicFile.__name__, "dialogconfig.ui")
        log.debug(str)
        uic.loadUi(str, self)
        self.__initSignal__()
        self.lineEditHost.setText(host)
        self.spinBoxPort.setValue(port)
        self.spinBoxID.setValue(id)
    def __del__(self):
        log.debug("Dialog config destruction")
    def __initSignal__(self):
        self.pushButtonConnect.clicked.connect(self.pushButtonConnectClicked)
        self.pushButtonCancel.clicked.connect(self.pushButtonCancelClicked)
    def pushButtonConnectClicked(self):
        self.labelStatus.setText("Connecting")
        handler = modbusRTUOverTCP.Handler(self.lineEditHost.text(), self.spinBoxPort.value(), self.spinBoxID.value())
        response = handler.connect()
        if (response):
            self.handlerConnection = handler
            self.accept()
        else:
            self.labelStatus.setText("Error")
    def __checkConnectionTask__(self):
        handler = modbusRTUOverTCP.Handler(self.lineEditHost.text(), self.spinBoxPort.value(), self.spinBoxID.value())
        response = handler.connect()
        return response
    def __checkConnectionCallBack__(self):
        if (response):
            self.handlerConnection = handler
            self.accept()
        else:
            self.labelStatus.setText("Error")

    def pushButtonCancelClicked(self):
        self.reject()
    def getHandlerConnection(self):
        return self.handlerConnection