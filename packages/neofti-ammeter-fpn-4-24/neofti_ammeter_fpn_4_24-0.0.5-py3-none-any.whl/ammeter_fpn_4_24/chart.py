import numpy as np
import pyqtgraph as pg
from PyQt6 import QtCore
import logging

log = logging.getLogger()

class Chart(pg.GraphicsLayoutWidget):
    def __init__(self,parent=None):
        super().__init__(parent = parent,title = "Chart")
        log.debug("Create chart")
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'k')
        self.labelAxisStyle = {'color': '#000', 'font-size': '14pt'}
        self.titlePlotStyle = {'color': '#000', 'font-size': '20pt'}
        color='w'
        self.setBackground(color)
        self.mainPlot = self.addPlot()
        self.mainPlot.setTitle("Real time charting", **self.titlePlotStyle)
        self.setLabelByTypeData("Ampere")
        self.mainPlot.setMouseEnabled(x=False,y=False)
        #self.mainPlot.addLegend()#offset=(30,30))
        legend = pg.LegendItem((80,60), offset=(70,20))
        legend.setParentItem(self.mainPlot)
        self.channel1Item:pg.PlotDataItem = self.mainPlot.plot(pen=(170,120,0), name="Channel 1")
        self.channel2Item:pg.PlotDataItem = self.mainPlot.plot(pen=(0,120,120), name="Channel 2")
        self.channel3Item:pg.PlotDataItem = self.mainPlot.plot(pen=(0,255,50), name="Channel 3")
        self.channel4Item:pg.PlotDataItem = self.mainPlot.plot(pen=(150,100,100), name="Channel 4")
        legend.addItem(self.channel1Item, 'Channel 1')
        legend.addItem(self.channel2Item, 'Channel 2')
        legend.addItem(self.channel3Item, 'Channel 3')
        legend.addItem(self.channel4Item, 'Channel 4')

    def setLabelByTypeData(self,type:str):
        if type == "Ampere":
            self.mainPlot.setLabel('left', "Ampere", units="A", **self.labelAxisStyle)
            self.mainPlot.setLabel('bottom', "Time", units="sec", **self.labelAxisStyle)
        if type == "Coulomb":
            self.mainPlot.setLabel('left', "Coulomb", units="C", **self.labelAxisStyle)
            self.mainPlot.setLabel('bottom', "Time", units="sec", **self.labelAxisStyle)
        elif type == "Fluence":
            self.mainPlot.setLabel('left', "Fluence", units="P", **self.labelAxisStyle)
            self.mainPlot.setLabel('bottom', "Time", units="sec", **self.labelAxisStyle)

    def setDataCh1(self,x,y):
        self.channel1Item.setData(x=x,y=y)
    def setDataCh2(self,x,y):
        self.channel2Item.setData(x=x,y=y)
    def setDataCh3(self,x,y):
        self.channel3Item.setData(x=x,y=y)
    def setDataCh4(self,x,y):
        self.channel4Item.setData(x=x,y=y)
    def clearData(self):
        self.channel1Item.clear()
        self.channel2Item.clear()
        self.channel3Item.clear()
        self.channel4Item.clear()
        self.mainPlot.replot()
    def setAutoScaleX(self,mode):
        self.mainPlot.enableAutoRange('x',mode)
        self.mainPlot.setMouseEnabled(x=not mode)
    def setAutoScaleY(self,mode):
        self.mainPlot.enableAutoRange('y',mode)
        self.mainPlot.setMouseEnabled(y=not mode)
    def getRangeX(self):
        return self.mainPlot.getAxis('bottom').range
    def getRangeY(self):
        return self.mainPlot.getAxis('left').range
    def setRangeY(self,min,max):
        self.mainPlot.setYRange(min,max,padding=0)
    def setRangeX(self,min,max):
        self.mainPlot.setXRange(min,max,padding=0)
