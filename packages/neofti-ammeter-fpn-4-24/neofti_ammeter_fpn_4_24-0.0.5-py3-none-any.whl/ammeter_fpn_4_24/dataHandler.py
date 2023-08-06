#Project module

#Third party module

import numpy as np
#Python module



ELEMENTARYCHARGE:float = 1.6 *10**-19

def __getAmperByVoltageCh1__(voltage:float):
    resistance = 10**9
    return (((voltage+1300)/(10**6))/resistance)
def __getAmperByVoltageCh2__(voltage:float):
    resistance = 10**8
    return ((voltage/(10**6))/resistance)
def __getAmperByVoltageCh3__(voltage:float):
    resistance = 10**7
    return ((voltage/(10**6))/resistance)
def __getAmperByVoltageCh4__(voltage:float):
    resistance = 10**6
    return ((voltage/(10**6))/resistance)
def getAmpereByVoltage(data):
    result = list()
    result.append(__getAmperByVoltageCh1__(data[0]))
    result.append(__getAmperByVoltageCh2__(data[1]))
    result.append(__getAmperByVoltageCh3__(data[2]))
    result.append(__getAmperByVoltageCh4__(data[3]))
    return result
def getFluenceByCoulomb(data,chargeNumberZ):
    result = list()
    result.append((data[0])/(chargeNumberZ*ELEMENTARYCHARGE))
    result.append((data[1])/(chargeNumberZ*ELEMENTARYCHARGE))
    result.append((data[2])/(chargeNumberZ*ELEMENTARYCHARGE))
    return result
def getAmperesByVoltages(data):
    result = list()
    for item in data:
        result.append(getAmpereByVoltage(item))
    return result
def getFluencesByCoulombs(data,chargeNumberZ):
    result = list()
    for item in data:
        result.append(getFluenceByCoulomb(item,chargeNumberZ))
    return result

    