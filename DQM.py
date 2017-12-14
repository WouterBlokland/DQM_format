#!/usr/bin/env python
#
# # Ensure that a division will return a float
from __future__ import division

import ROOT
import itertools as it
import re
import numpy
import time
import math
import glob
import sys
import os
from subprocess import call

# Import default config file
# Not needed here just for dumb editor not to complain about config not existing
import config_dqm as conf

# define fixed time vector of conf.recordLength ns
time = ROOT.TVectorD(conf.recordLength)
for i in range(0, conf.recordLength):
    time[i] = i


def loadFiles(dir):
    '''Returns nCompleteEvent (int), fileList (list[lines])
    '''
    nEvents = 0
    files = []
    for iChan in range(0, conf.nChannels):
        file = dir + conf.dataFileFormat % iChan
        lines = [line.rstrip('\n') for line in open(file, 'r')]
        nEventsInFile = getCompleteEvents(lines)
        if iChan > 0:
            assert nEventsInFile == nEvents, sys.exit(
                '[ERROR]: Channels {} and {} don\'t have same number of event!: {}, {} respectively.'.format(
                    iChan, iChan - 1, nEvents, nEventsInFile))
        nEvents = nEventsInFile
        files.append(lines)
    return int(nEvents), files


def getCompleteEvents(lines):
    ''' Return number of complete events from the files
        If last event not complete (len(lastEvent)< (recordLength + headerSize)) get rid of it
    Args
        lines (list[str]): lines read from a waveform file
    Returns
        int: number of completed events
    '''
    nEvents = len(lines) / (conf.recordLength + conf.headerSize)
    if nEvents.is_integer() is False:
        lines = removePartialEvent(lines)
        nEvents = len(lines) / (conf.recordLength + conf.headerSize)
        assert nEvents.is_integer() is True, sys.exit('[ERROR]: What the flying duck?')
    return int(nEvents)


def removePartialEvent(lines):
    ''' Return truncated file content with only complete event (List)
    '''
    nLinesPartialEvt = len(lines) % (conf.recordLength + conf.headerSize)
    print '[WARNING]: Last event was not recorded properly, only {} line recorded - Removing event...'.format(
        nLinesPartialEvt)
    del lines[-nLinesPartialEvt:]
    assert len(lines) % (conf.recordLength + conf.headerSize) == 0, sys.exit('[ERROR]: You still have partial event')
    return lines


def getInt(s):
    return int(re.search(r'\d+', s).group())


def getFloat(s):
    return float(re.search(r'\d+\.\d+', s).group())


################################################################################


def run(runid):

    dir = conf.dataDir + str(runid) + '/'
    print "Analyze run %s" % runid
    assert os.path.exists(dir) is True, sys.exit('[ERROR]: Directory `{}` not found...exiting'.format(dir))

    for hvPoint in os.listdir(dir):
        try:
            assert hvPoint.isdigit()
        except AssertionError:
            print 'Warning - skipping folder "{}"'.format(hvPoint)
            continue
        HVdir = dir + hvPoint + '/'
        print "Running in dir %s" % HVdir

        tFull = ROOT.TTree("data", "data")  # full events
        tStrip = ROOT.TTree("data", "data")  # stripped events

        evNum = numpy.zeros(1, dtype=int)
        trgTime = numpy.zeros(1, dtype=int)

        tFull.Branch("evNum", evNum, "evNum/I")
        tFull.Branch("trgTime", trgTime, "trgTime/I")

        tStrip.Branch("evNum", evNum, "evNum/I")
        tStrip.Branch("trgTime", trgTime, "trgTime/I")

        pulses = []
        for iChan in range(0, conf.nChannels):
            pulse = ROOT.vector('double')()
            pulses.append(pulse)

            tFull.Branch("pulse_ch%d" % iChan, pulses[iChan])  # , "pulse[conf.recordLength]/F"
            tStrip.Branch("pulse_ch%d" % iChan, pulses[iChan])  # , "pulse[conf.recordLength]/F"

        # load all waves into memory
        nEvents, files = loadFiles(HVdir)

        print "LOOOOP", nEvents

        ff = math.ceil(nEvents / (nEvents * 0.05))
        entriesWritten = 0

        for iTime in range(0, len(files[0])):
            if "Record Length" in files[0][iTime]: continue
            elif "BoardID" in files[0][iTime]: continue
            elif "Channel" in files[0][iTime]: continue
            elif "Event Number" in files[0][iTime]: evNum[0] = getInt(files[0][iTime])
            elif "Pattern" in files[0][iTime]:
                continue
            elif "Trigger Time Stamp" in files[0][iTime]: trgTime[0] = getInt(files[0][iTime])
            elif "DC offset (DAC)" in files[0][iTime]: continue
            elif "Start Index Cell" in files[0][iTime]:
                continue
            else:
                for iChan in range(0, conf.nChannels):
                    pulses[iChan].push_back(float(files[iChan][iTime]))

            # write and clean
            if (iTime + 1) % (conf.recordLength + conf.headerSize) == 0:
                entriesWritten += 1
                tFull.Fill()

                if entriesWritten % ff == 0:
                    print "Fill stripped {} {} {:4.2f}%".format(iTime, tFull.GetEntries(),
                                                                tFull.GetEntries() / nEvents * 100)
                    tStrip.Fill()

                #print "WRITE", evNum, trgTime
                for iChan in range(0, conf.nChannels):
                    pulses[iChan].clear()

        f1 = ROOT.TFile("%s/%s.root" % (HVdir, hvPoint), "recreate")
        tFull.Write()
        time.Write("time")
        f1.Close()

        f2 = ROOT.TFile("%s/%s.dqm.root" % (HVdir, hvPoint), "recreate")
        tStrip.Write()
        time.Write("time")
        f2.Close()

        files = None  # clear memory


# PROBLEMATIC:
# BINARY: 2381, 2380

configFile = "config_dqm"  # Default config file if none is given on cli
# --- Load configuration File
configFile = sys.argv[1]
try:
    exec ("import {} as conf".format(configFile))
except (ImportError, SyntaxError):
    sys.exit("[DQM.py] - Cannot import config file '{}'".format(configFile))  # --- /Load configuration File

runList = []
if len(sys.argv) > 2:
    if isinstance(sys.argv[2], list):
        runList = sys.argv[2]
    else:
        for iRun in range(2, len(sys.argv)):
            runList.append(sys.argv[iRun])
else:
    runList = conf.runList

if len(runList) == 0:
    assert os.path.exists(conf.dataDir) is True, sys.exit('[ERROR]: Directory `{}` not found...exiting'.format(
        conf.dataDir))
    runList = os.listdir(conf.dataDir)

for runid in runList:
    print 'runid: ', runid
    run(runid)

# runs = [2375, 2379, 2383, 2385, 2388, 2390, 2392, 2394, 2396, 2398, 2400, 2402, 2404]  # first -> OK
# runs = [2406, 2408, 2410, 2412, 2414, 2416, 2418, 2420, 2422, 2424, 2426, 2428, 2430, 2432]  # second -> OK
# runs = [2377, 2382, 2384, 2386, 2389, 2391, 2393, 2395, 2397, 2399, 2401, 2403, 2405] # third -> OK
# runs = [2407, 2409, 2411, 2413, 2415, 2417, 2419, 2421, 2423, 2425, 2427, 2429, 2431, 2433] # fourth -> OK

# runs = [2381]

# runs = [ 2389, 2391, 2393, 2395, 2397, 2399, 2401, 2403, 2405] # third

# runs = [2398, 2402, 2399, 2419, 2396, 2395, 2424, 2401, 2397, 2393, 2392, 2390]
# runs = [2409, 2403, 2412, 2420, 2413, 2416, 2423]
# runs = [2410, 2404, 2411, 2421, 2414, 2415, 2422]
# runs = [2564]
