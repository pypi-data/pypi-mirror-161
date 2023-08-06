#Project module
from ammeter_fpn_4_24.ui import uic as uicFile
from ammeter_fpn_4_24 import chart
#Third party module
from PyQt6 import QtCore, QtWidgets,uic
import pyqtgraph as pg
import numpy as np
#Python module
from pkg_resources import resource_listdir,resource_filename
import logging
from enum import Enum


log = logging.getLogger()

class ModeInterface(Enum):
    DEFAULT = (True, True, "Start",True)
    RUNNING = (False,False,"Stop",False)
    def __init__(self,connectionControlEnabled:bool,outputDataControlEnabled:bool,nameStartStopButton:str,preStartParameters:bool):
        self.connectionControlEnabled = connectionControlEnabled
        self.outputDataControlEnabled = outputDataControlEnabled
        self.nameStartStopButton = nameStartStopButton
        self.preStartParameters = preStartParameters

class MainWindow(QtWidgets.QMainWindow):
    startSignal = QtCore.pyqtSignal()
    stopSignal = QtCore.pyqtSignal()
    writeTimeGateSignal = QtCore.pyqtSignal(int)
    openDialogConfigSignal = QtCore.pyqtSignal()
    typeShowedDataChanged = QtCore.pyqtSignal()
    clearDataSignal = QtCore.pyqtSignal()
    def __init__(self,parent=None):
        super().__init__(parent)
        log.debug("Init main window")
        str = resource_filename(uicFile.__name__, "mainwindow.ui")
        log.debug(str)
        uic.loadUi(str, self)
        self.__initChart__()
        self.__initSignal__()
        self.setMode(ModeInterface.DEFAULT)

        self.doubleSpinBoxIntegral1 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxIntegral1.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxIntegral1.setReadOnly(True)
        self.doubleSpinBoxIntegral1.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutIntegralCh1.addWidget(self.doubleSpinBoxIntegral1)
        self.doubleSpinBoxIntegral2 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxIntegral2.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxIntegral2.setReadOnly(True)
        self.doubleSpinBoxIntegral2.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutIntegralCh2.addWidget(self.doubleSpinBoxIntegral2)
        self.doubleSpinBoxIntegral3 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxIntegral3.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxIntegral3.setReadOnly(True)
        self.doubleSpinBoxIntegral3.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutIntegralCh3.addWidget(self.doubleSpinBoxIntegral3)
        self.doubleSpinBoxIntegral4 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxIntegral4.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxIntegral4.setReadOnly(True)
        self.doubleSpinBoxIntegral4.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutIntegralCh4.addWidget(self.doubleSpinBoxIntegral4)

        self.doubleSpinBoxMean1 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxMean1.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxMean1.setReadOnly(True)
        self.doubleSpinBoxMean1.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutMeanCh1.addWidget(self.doubleSpinBoxMean1)
        self.doubleSpinBoxMean2 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxMean2.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxMean2.setReadOnly(True)
        self.doubleSpinBoxMean2.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutMeanCh2.addWidget(self.doubleSpinBoxMean2)
        self.doubleSpinBoxMean3 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxMean3.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxMean3.setReadOnly(True)
        self.doubleSpinBoxMean3.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutMeanCh3.addWidget(self.doubleSpinBoxMean3)
        self.doubleSpinBoxMean4 = pg.SpinBox(value=0, suffix='A', siPrefix=True)
        self.doubleSpinBoxMean4.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.doubleSpinBoxMean4.setReadOnly(True)
        self.doubleSpinBoxMean4.setMinimumSize(QtCore.QSize(60, 30))
        self.verticalLayoutMeanCh4.addWidget(self.doubleSpinBoxMean4)
        
        self.interfaceSigChangedOff = False
        self.typeDataShow = "Ampere"
    def __initSignal__(self):
        self.pushButtonStartStopRun.clicked.connect(self.startStopRunClicked)
        #self.checkBoxAutoRead.toggled.connect(self.checkBoxAutoReadToggled)
        #self.pushButtonWrite.clicked.connect(self.pushButtonWriteClicked)
        self.actionConnectionEdit.triggered.connect(self.openDialogConnectionConfig)
        self.checkBoxAutoScaleX.toggled.connect(self.__chart.setAutoScaleX)
        self.checkBoxAutoScaleY.toggled.connect(self.__chart.setAutoScaleY)
        self.checkBoxAutoScaleX.toggled.connect(self.checkBoxAutoScaleXToggled)
        self.checkBoxAutoScaleY.toggled.connect(self.checkBoxAutoScaleYToggled)
        self.__chart.mainPlot.sigRangeChanged.connect(self.chartRangeChanged)
        self.spinBoxXMax.valueChanged.connect(self.spinBoxXMaxValueChanged)
        self.spinBoxXMin.valueChanged.connect(self.spinBoxXMinValueChanged)
        self.spinBoxYMax.valueChanged.connect(self.spinBoxYMaxValueChanged)
        self.spinBoxYMin.valueChanged.connect(self.spinBoxYMinValueChanged)
        self.pushButtonSaveFolder.clicked.connect(self.openGetFolderDialog)
        #self.pushButtonChangeGraph.clicked.connect(self.pushButtonChangeGraphClicked)
        self.pushButtonClear.clicked.connect(self.pushButtonClearClicked)

    def __initChart__(self):
        self.__chart = chart.Chart(self)
        self.verticalLayout_4.addWidget(self.__chart)
    def setDataChart(self,x,data):
        dataCh1 = list()
        dataCh2 = list()
        dataCh3 = list()
        dataCh4 = list()
        for item in data:
            dataCh1.append(item[0])
            dataCh2.append(item[1])
            dataCh3.append(item[2])
            dataCh4.append(item[3])
        self.__chart.setDataCh1(x, dataCh1)
        self.__chart.setDataCh2(x, dataCh2)
        self.__chart.setDataCh3(x, dataCh3)
        self.__chart.setDataCh4(x, dataCh4)
    def getChart(self):
        return self.__chart
    def checkBoxAutoReadToggled(self,value:bool):
        self.spinBox_readTime.setEnabled(not value)
    def setMode(self,mode:ModeInterface):
        log.debug("Change mode to {0}".format(mode._name_))
        self.__currentModeInterface = mode
        self.actionConnectionEdit.setEnabled(mode.connectionControlEnabled)
        self.pushButtonSaveFolder.setEnabled(mode.outputDataControlEnabled)
        self.checkBoxWrite.setEnabled(mode.outputDataControlEnabled)
        self.pushButtonStartStopRun.setText(mode.nameStartStopButton)
        self.spinBoxZ.setEnabled(mode.preStartParameters)
    def startStopRunClicked(self):
        log.debug("StartStopButton is clicked")
        if self.__currentModeInterface == ModeInterface.DEFAULT:
            self.setMode(ModeInterface.RUNNING)
            self.startSignal.emit()
        elif self.__currentModeInterface == ModeInterface.RUNNING:
            self.setMode(ModeInterface.DEFAULT)
            self.stopSignal.emit()
    def showMessage(self,message:str,isError:bool=False):
        msgBox = QtWidgets.QMessageBox(self)
        if isError:
            msgBox.setText(message)
            msgBox.setInformativeText("")
            #msgBox.setStandardButtons(QtWidgets.QMessageBox.OK)
        else:
            msgBox.setText(message)
            msgBox.setInformativeText("")
            #msgBox.setStandardButtons(QtWidgets.QMessageBox.OK)
        response = msgBox.exec()
        return response
    def pushButtonWriteClicked(self):
        self.writeTimeGateSignal.emit(self.spinBoxTimeGate.value())
    def setTimeGate(self,value:int):
        pass
        #self.spinBoxTimeGate.setValue(value)
    def openDialogConnectionConfig(self):
        self.openDialogConfigSignal.emit()
    def chartRangeChanged(self):
        self.interfaceSigChangedOff = True
        #if not self.checkBoxAutoScaleX.isChecked(): return
        x = self.__chart.getRangeX()
        self.spinBoxXMin.setValue(x[0])
        self.spinBoxXMax.setValue(x[1])
        
        #if not self.checkBoxAutoScaleY.isChecked(): return
        y = self.__chart.getRangeY()
        self.spinBoxYMin.setValue(y[0])
        self.spinBoxYMax.setValue(y[1])
        self.interfaceSigChangedOff = False
    def checkBoxAutoScaleXToggled(self, mode:bool):
        self.spinBoxXMin.setEnabled(not mode)
        self.spinBoxXMax.setEnabled(not mode)
    def checkBoxAutoScaleYToggled(self, mode:bool):
        self.spinBoxYMin.setEnabled(not mode)
        self.spinBoxYMax.setEnabled(not mode)
    def spinBoxXMinValueChanged(self,value:float):
        if self.checkBoxAutoScaleX.isChecked() or self.interfaceSigChangedOff: return
        self.__chart.setRangeX(self.spinBoxXMin.value(),self.spinBoxXMax.value())
    def spinBoxXMaxValueChanged(self,value:float):
        if self.checkBoxAutoScaleX.isChecked() or self.interfaceSigChangedOff: return
        self.__chart.setRangeX(self.spinBoxXMin.value(),self.spinBoxXMax.value())
    def spinBoxYMinValueChanged(self,value:float):
        if self.checkBoxAutoScaleY.isChecked() or self.interfaceSigChangedOff: return
        self.__chart.setRangeY(self.spinBoxYMin.value(),self.spinBoxYMax.value())
    def spinBoxYMaxValueChanged(self,value:float):
        if self.checkBoxAutoScaleY.isChecked() or self.interfaceSigChangedOff: return
        self.__chart.setRangeY(self.spinBoxYMin.value(),self.spinBoxYMax.value())
    def setCycleAndIntegralData(self,valueCycle:int,valueCh1,valueCh2,valueCh3,valueCh4):
        self.spinBoxCycle.setValue(valueCycle)
        self.doubleSpinBoxIntegral1.setValue(valueCh1)
        self.doubleSpinBoxIntegral2.setValue(valueCh2)
        self.doubleSpinBoxIntegral3.setValue(valueCh3)
        self.doubleSpinBoxIntegral4.setValue(valueCh4)
        self.doubleSpinBoxMean1.setValue(valueCh1/valueCycle)
        self.doubleSpinBoxMean2.setValue(valueCh2/valueCycle)
        self.doubleSpinBoxMean3.setValue(valueCh3/valueCycle)
        self.doubleSpinBoxMean4.setValue(valueCh4/valueCycle)
    def getPathSaveFolder(self):
        return self.lineEditSaveFolder.text()
    def setPathSaveFolder(self, text):
        self.lineEditSaveFolder.setText(text)
    def openGetFolderDialog(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory",directory=self.lineEditSaveFolder.text()))
        if file != "":
            self.setPathSaveFolder(file)
    def pushButtonClearClicked(self):
        self.__chart.clearData()
        self.clearDataSignal.emit()
    def pushButtonChangeGraphClicked(self):
        if self.typeDataShow == "Fluence":
            self.typeDataShow = "Coulomb"
            self.pushButtonChangeGraph.setText("Coulomb")
            self.setTypeData("Coulomb")
        elif self.typeDataShow == "Coulomb":
            self.typeDataShow = "Fluence"
            self.pushButtonChangeGraph.setText("Fluence")
            self.setTypeData("Fluence")
        self.typeShowedDataChanged.emit()
    def getChargeNumber(self):
        return self.spinBoxZ.value()
    def setTypeData(self,type:str):
        self.__chart.setLabelByTypeData(type)
        if type == "Coulomb":
            sufix = "C"
        elif type =="Fluence":
            sufix = "P"
        self.doubleSpinBoxIntegral1.setSuffix(sufix)
        self.doubleSpinBoxIntegral2.setSuffix(sufix)
        self.doubleSpinBoxIntegral3.setSuffix(sufix)
        self.doubleSpinBoxMean1.setSuffix(sufix)
        self.doubleSpinBoxMean2.setSuffix(sufix)
        self.doubleSpinBoxMean3.setSuffix(sufix)