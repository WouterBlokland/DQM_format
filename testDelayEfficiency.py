#!/usr/bin/env python
# Put Number of files from efficiency to analyze ( NumFiles = )
# Use environmental variables:
# DigiCodeDebug 0 or 1 for no extra message to print
# DigiCodeFirst and DigiCodeLast  first and last event to analyze
# Salvador Carrillo Oct/2017 EcoGas Test at Beatrice Lab

# Ensure that a division will return a float
from __future__ import division

import ROOT
import sys
import os
import numpy as np
import digiHelper as dH

# Import default config file
# Not needed here just for dumb editor not to complain about config not existing
import config_dqm as conf
configFile = "config_dqm"  # Default config file if none is given on cli
# --- Load configuration File
configFile = sys.argv[1]
try:
    exec ("import {} as conf".format(configFile))
    print 'success'
except (ImportError, SyntaxError):
    sys.exit("[EventDisplay.py] - Cannot import config file '{}'".format(configFile))
# --- /Load configuration File

###########################################
# analyzer.py works opening several files

# inputFile = [0 for i in range(16)]

# inputFile[9] = "HVSCAN/002593/HV2/HV2.root"

# for num in range(1, NumFiles + 1):
#     if (debug > 0):
#         print num
#     fIn[num] = ROOT.TFile(inputFile[num])  # open ROOT file
#     data[num] = fIn[num].Get("data")  # get the data tree
# time = fIn[num].Get("time")  # get the time vector

# run = HVPoint


def getBaselineAndDeviation(pulses):
    mean = {}
    stdv = {}
    for iPulse in range(0, conf.nChannels):
        assert conf.recordLength == len(pulses[iPulse]), sys.exit('ERROR: Weird data in channel' + iPulse)
        mean[iPulse] = np.mean(pulses[iPulse][:100])
        stdv[iPulse] = np.std(pulses[iPulse][:100]) * 10.0
    return mean, stdv


def removeBaseLine(pulseList, baseLineList):
    ''' pulses, baseLine
    '''
    newPulses = {}
    for iPulse in range(0, len(pulseList)):
        newPulses[iPulse] = pulseList[iPulse] - baseLineList[iPulse]
    return newPulses


def getTimeOverThreshold(pulse, pulsePolarity, mean, stdv, beginSignal):
    '''
    '''
    assert beginSignal < conf.recordLength, sys.exit('[ERROR] Found a signal after end of record, signalTime = ',
                                                     beginSignal)
    tot = 0
    iTime = beginSignal
    print '\t pol {} - pulse {}'.format(pulsePolarity, pulse[iTime] - mean),
    while (pulse[iTime] - mean) * pulsePolarity > stdv and iTime < conf.recordLength:
        tot = tot + 1
        iTime = iTime + 1
    print '\t tot {}'.format(tot),
    return tot


def getIntegralOverThreshold(pulse, pulsePolarity, mean, beginSignal, endSignal):
    '''
    '''
    assert beginSignal < conf.recordLength, sys.exit('[ERROR] Found a signal after end of record, signalTime = ',
                                                     beginSignal)
    total = 0
    for iTime in range(beginSignal, endSignal):
        total += (pulse[iTime] - mean) * pulsePolarity
    print '\t total {}'.format(total)
    return total

# Loop over all the Data Files
def computeEfficiency(runFile):
    fIn = ROOT.TFile(runFile, "READ")
    tree = fIn.Get('data')
    # Create the list of branches to read from fIn
    pulseBranchList = dH.getListOfPulseBranches(tree, conf.nChannels)

    try:
        debug = int(os.environ['DigiCodeDebug'])
    except KeyError:
        debug = 0

    try:
        first = int(os.environ['DigiCodeFirst'])
        last = int(os.environ['DigiCodeLast'])
    except KeyError:
        first = 0
        last = 0

    if last == 0:
        last = tree.GetEntries()

    assert last != first, sys.exit('Error: First and last events are the same, can\'t computer efficiency')
    eff = 0
    evtProcessed = 0
    for event in tree:
        evtProcessed += 1
        time = dH.vector2list(fIn.time)

        pulse = {}
        mean = {}
        stdv = {}
        for iChan in range(0, conf.nChannels):
            pulse[iChan] = dH.vector2list(pulseBranchList[iChan])

        trgTime = event.trgTime
        evNum = event.evNum

        # Get baseline + deviation of 10sigma
        mean, stdv = getBaselineAndDeviation(pulse)
        print 'mean {} stdv {}'.format(mean, stdv)
        newPulses = removeBaseLine(pulse, mean)
        print 'newPulse: ', newPulses
        sys.exit(0)
        # for iPulse in range(0, conf.nChannels):
        #     assert conf.recordLength == len(pulse[0]), sys.exit('ERROR: Weird data in channel' + iPulse)
        #     mean[iPulse] = np.mean(pulse[iPulse][:100])
        #     stdv[iPulse] = np.std(pulse[iPulse][:100]) * 10.0

        multiplicity = 0
        found = [False] * conf.nChannels
        reflexion = [False] * conf.nChannels
        # Loop on time
        for iTime in range(0, conf.recordLength):
            b = 0
            if (debug > 0):
                print "--> " + str(iTime)
            for iChan in range(0, conf.nChannels):
                if found[iChan] is True or reflexion[iChan] is True:
                    continue
                if (debug > 0):
                    print "\t --> " + str(iChan),
                if abs(pulse[iChan][iTime] - mean[iChan]) > stdv[iChan]:  # Found Signal
                    if (pulse[iChan][iTime] - mean[iChan]) * (conf.pulsePolarity) > 0:  # Signal has expected polarity
                        print '\t --> Evt {} @ {} chan {}: Same pol '.format(evNum, iTime, iChan),
                        timeOverThresh = getTimeOverThreshold(pulse[iChan], conf.pulsePolarity, mean[iChan],
                                                              stdv[iChan], iTime)
                        charge = getIntegralOverThreshold(pulse[iChan], conf.pulsePolarity, mean[iChan], iTime,
                                                          iTime + timeOverThresh)

                        if timeOverThresh > (
                                conf.timeOverThresholdLimit * conf.sampling * 1E-3):  # tot in ns, sampling in MS/s
                            found[iChan] = True
                            multiplicity += 1
                            # if (debug > 0):
                            print "\t\t Evt '{}': Found at {} in chan {}, mul:{} tot:{}".format(
                                evNum, iTime, iChan, multiplicity, timeOverThresh)
                    else:  # Signal has reversed polarity -> reflexion?
                        print '\t --> Evt {} @ {} chan {}: Rev pol '.format(evNum, iTime, iChan),
                        timeOverThresh = getTimeOverThreshold(pulse[iChan], -conf.pulsePolarity, mean[iChan], stdv[iChan], iTime)
                        charge = getIntegralOverThreshold(pulse[iChan], -conf.pulsePolarity, mean[iChan], iTime,
                                                          iTime + timeOverThresh)
                        if timeOverThresh > (
                                conf.timeOverThresholdLimit * conf.sampling * 1E-3):  # tot in ns, sampling in MS/s
                            reflexion[iChan] = True

        if multiplicity > 0:
            eff += 1
        if (debug > 0):
            print ""

        if evtProcessed % np.ceil((last - first) * 0.05) == 0:
            print '{}% done :'.format(int(evtProcessed / (last - first) * 100)),
            print "Mul = {} - Efficiency = {}/{} => {:4.2f}%".format(
                multiplicity, eff, evtProcessed, 100. * eff /
                evtProcessed)  # + str(eff) + "/" + str(evtProcessed) + " => " + str(100. * eff / evtProcessed) + "%"

        if not found and debug > 0:
            print "Event not efficient : " + str(evNum)

    # Efficiency and Error
    Efficiency = 1. * eff / (last - first)
    error = np.sqrt(1.0 * Efficiency * (1 - Efficiency) / (last - first))
    # Print in Porcentage
    if (debug > 0):
        print "HV" + str(runFile) + " " + str(eff) + " " + str(last - first) + " " + str(100. * Efficiency) + " " + str(
            100. * error)

    fIn.Close()
    return Efficiency, error

# for num in range(1, NumFiles):
#     fIn[num].Close()


def main():
    runList = []
    if len(sys.argv) > 2:
        if isinstance(sys.argv[2], list):
            runList = sys.argv[2]
        else:
            for iRun in range(2, len(sys.argv)):
                runList.append(sys.argv[iRun])
    else:
        runList = conf.runList

    runEffDic = {}
    for runId in runList:
        runEffDic[runId] = []
        print 'runId: ', runId
        dir = conf.dataDir + str(runId) + '/'
        print "Analyze run %s" % runId
        assert os.path.exists(dir) is True, sys.exit('[ERROR]: Directory `{}` not found...exiting'.format(dir))
        for hvPoint in os.listdir(dir):  # loop over all HV
            try:
                assert hvPoint.isdigit()
            except AssertionError:
                print 'Warning - skipping folder "{}"'.format(hvPoint)
                continue

            HVdir = dir + hvPoint + '/'
            print "\nRunning in dir %s" % HVdir
            eff, effErr = computeEfficiency(HVdir + hvPoint + '.root')
            runEffDic[runId].append({'HV': hvPoint, 'Efficiency': eff, 'Error': effErr})
            print 'run {} - {}V - Eff: {:4.2f} +- {:4.2f} %'.format(runId, hvPoint, eff * 100, effErr * 100)

    toPrint = ' SUMMARY '
    printLenght = 64
    toCenter = (printLenght - len(toPrint)) / 2
    print '\n', '-' * printLenght
    print '-' * int(toCenter), toPrint, '-' * int(toCenter)
    print '-' * printLenght

    for runId, hvPointList in runEffDic.iteritems():
        print 'run', runId
        for hvPoint in hvPointList:
            print '\t{}V - Eff: {:4.2f} +- {:4.2f} %'.format(hvPoint['HV'], hvPoint['Efficiency'] * 100,
                                                             hvPoint['Error'] * 100)


if __name__ == "__main__":
    main()




# def compareChans(chan1,chan2):
