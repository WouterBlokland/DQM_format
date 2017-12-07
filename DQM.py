import ROOT 
import itertools as it
import re
import numpy
import time
import math
import glob
import sys,os
from subprocess import call

# define fixed time vector of conf.recordLength ns
time = ROOT.TVectorD(conf.recordLength)
for i in range(0, conf.recordLength):
    time[i] = i

# Import default config file
# Not needed here just for dumb editor not to complain about config not existing
import config_dqm as conf

def loadFiles(dir):
    nEvents = 0
    files = []
    for i in range(0, conf.nChannels):


        lines = [line.rstrip('\n') for line in open("%s/wave_%d.txt" % (dir, i))]
        files.append(lines)
        nEvents = len(lines)
    nEvents = len(lines) / (conf.recordLength + conf.headerSize)

    return nEvents, files
    



def getInt(s):
    return int(re.search(r'\d+', s).group())
    
def getFloat(s):
    return float(re.search(r'\d+\.\d+', s).group())


################################################################################



def run(runid):

    dir = conf.dataDir % runid
    print "Analyze run %s" % runid

    for hvPoint in os.listdir(dir):


        HVdir = dir + hvPoint + '/'
        print "Running in dir %s" % HVdir

        tFull = ROOT.TTree("data", "data") # full events
        tStrip = ROOT.TTree("data", "data") # stripped events

        evNum = numpy.zeros(1, dtype=int)
        trgTime = numpy.zeros(1, dtype=int)  

        tFull.Branch("evNum", evNum, "evNum/I")
        tFull.Branch("trgTime", trgTime, "trgTime/I")

        tStrip.Branch("evNum", evNum, "evNum/I")
        tStrip.Branch("trgTime", trgTime, "trgTime/I")
        
        pulses = []
        for i in range(0, conf.nChannels):
            pulse = ROOT.vector('double')()
            pulses.append(pulse)
            

            tFull.Branch("pulse_ch%d" % i, pulses[i])  # , "pulse[conf.recordLength]/F"
            tStrip.Branch("pulse_ch%d" % i, pulses[i])  # , "pulse[conf.recordLength]/F"

        ### load all waves into memory
        nEvents, files = loadFiles(HVdir)

        print "LOOOOP", nEvents

        ff = math.ceil(nEvents / (nEvents*0.05))
        entriesWritten = 0

        for i in range(0, len(files[0])):

            

            if "Record Length" in files[0][i]: continue
            elif "BoardID" in files[0][i]: continue
            elif "Channel" in files[0][i]: continue
            elif "Event Number" in files[0][i]: evNum[0] = getInt(files[0][i])
            elif "Pattern" in files[0][i]: continue
            elif "Trigger Time Stamp" in files[0][i]: trgTime[0] = getInt(files[0][i])
            elif "DC offset (DAC)" in files[0][i]: continue
            elif "Start Index Cell" in files[0][i]: continue
            else:


                for j in range(0, conf.nChannels):
                    pulses[j].push_back(float(files[j][i]) * 1000 / 4096)

            # write and clean
            if (i + 1) % (conf.recordLength + conf.headerSize) == 0:

                entriesWritten += 1
                #if 1283 == entriesWritten: break

                tFull.Fill()
                

                if entriesWritten%ff== 0: 

                    print "Fill stripped ", i, tFull.GetEntries()
                    tStrip.Fill()

                #print "WRITE", evNum, trgTime


                for k in range(0, conf.nChannels):
                    pulses[k].clear()



        f1 = ROOT.TFile("%s/%s.root" % (HVdir, hvPoint), "recreate")
        tFull.Write()
        time.Write("time")
        f1.Close()

        f2 = ROOT.TFile("%s/%s.dqm.root" % (HVdir, hvPoint), "recreate")
        tStrip.Write()
        time.Write("time")
        f2.Close()

        files = None # clear memory
        







# PROBLEMATIC: 
# BINARY: 2381, 2380




configFile = "config_dqm"  # Default config file if none is given on cli
# --- Load configuration File
configFile = sys.argv[1]
try:
    exec ("import {0} as conf".format(configFile))
except (ImportError, SyntaxError):
    sys.exit("[{0}] - Cannot import config file '{1}'".format(scriptName, configFile))
# --- /Load configuration File

runList = conf.runList

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
