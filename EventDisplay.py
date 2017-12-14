#!/usr/bin/env python
#
# Ensure that a division will return a float
from __future__ import division
import ROOT
import sys
import copy
from array import array
import math
import os
import numpy as np

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

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


def vector2list(vec):
    ret = []
    for i in vec:
        ret.append(i)
    return ret


def removeHalfNoisePeak(pulse, mean, noiseLimit, pulsePolarity, peakTime, increment):
    iTime = peakTime
    while iTime > 0 and iTime < len(pulse) and (pulse[iTime] - mean) * pulsePolarity > noiseLimit:
        pulse[iTime] = mean  # Return to baseline
        iTime += increment
    return pulse


def removeNoisePeak(pulse, mean, noiseLimit, pulsePolarity, peakTime):
    pulse = removeHalfNoisePeak(pulse, mean, noiseLimit, pulsePolarity, peakTime, 1)
    pulse = removeHalfNoisePeak(pulse, mean, noiseLimit, pulsePolarity, peakTime, -1)
    return pulse


def removeNoisePeaks(pulse, mean, noiseLimit):
    ''' pulse is a single wave not the complete list
    '''
    print min(pulse), mean, min(pulse) - mean, noiseLimit
    print max(pulse), mean, max(pulse) - mean, noiseLimit
    if abs(min(pulse) - mean) > noiseLimit:
        print 'totototo'
        pulsePol = -1
        peakTime = np.argmin(pulse)
        pulse = removeNoisePeak(pulse, mean, noiseLimit, pulsePol, peakTime)

    if abs(max(pulse) - mean) > noiseLimit:
        print 'rorototototo'
        pulsePol = 1
        peakTime = np.argmax(pulse)
        pulse = removeNoisePeak(pulse, mean, noiseLimit, pulsePol, peakTime)

    return pulse


def getBaselineAndDeviation(pulses):
    mean = {}
    stdv = {}
    for iPulse in range(0, len(pulses)):
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


def makePrettyGraph(x, y, color):
    graph = copy.deepcopy(ROOT.TGraph(len(x), array('d', x), array('d', y)))
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(.4)
    graph.SetLineWidth(1)
    graph.SetLineColor(color)
    graph.SetMarkerColor(color)

    graph.GetYaxis().SetTitleFont(43)
    graph.GetYaxis().SetTitleSize(12)
    graph.GetYaxis().SetLabelFont(43)
    graph.GetYaxis().SetLabelSize(10)
    graph.GetYaxis().SetNdivisions(3)
    return graph


def makePlot(x, y, header, fname, count, miny, maxy):
    c = ROOT.TCanvas("c", "c", 1200, 900)
    c.Divide(2, int(math.ceil(conf.nChannels / 2)), 0.001, 0.002)
    graphs = []  # needed to store the TGraphs.. cannot overwrite as ROOT needs them to plot

    # loop over all strips
    mean = {}
    stdv = {}
    mini = {}
    maxi = {}
    noise = False
    axisCutOff = 10  # stdv
    mean, stdv = getBaselineAndDeviation(y)
    y = removeBaseLine(y, mean)
    mean, stdv = getBaselineAndDeviation(y)
    newY = copy.deepcopy(y)
    # newY = removeBaseLine(newY, [250] * conf.nChannels)

    for iPulse in range(0, conf.nChannels):
        assert conf.recordLength == len(y[iPulse]), sys.exit('ERROR: Weird data in channel' + iPulse)
        assert conf.recordLength == len(newY[iPulse]), sys.exit('ERROR: Weird data in channel' + iPulse)
        print 'y[{}]: {}'.format(iPulse, y[iPulse])
        print 'newY[{}]: {}'.format(iPulse, newY[iPulse])
        while abs(min(newY[iPulse])) > conf.noiseLimit * stdv[iPulse] or max(newY[iPulse]) > conf.noiseLimit * stdv[iPulse]:
            newY[iPulse] = removeNoisePeaks(newY[iPulse], mean[iPulse], conf.noiseLimit * stdv[iPulse])
        assert abs(min(newY[iPulse])) < conf.noiseLimit * stdv[iPulse], sys.exit('Fuck min {} {}'.format(
            min(newY[iPulse]), conf.noiseLimit * stdv[iPulse]))
        assert max(newY[iPulse]) < conf.noiseLimit * stdv[iPulse], sys.exit('Fuck max {} {}'.format(
            max(newY[iPulse]), conf.noiseLimit * stdv[iPulse]))
        mean[iPulse] = np.mean(y[iPulse][:100])
        stdv[iPulse] = np.std(y[iPulse][:100]) * 10.0
        mini[iPulse] = min(y[iPulse])
        maxi[iPulse] = max(y[iPulse])
        if mini[iPulse] < (mean[iPulse] - axisCutOff * stdv[iPulse]) or maxi[iPulse] > (
                mean[iPulse] + axisCutOff * stdv[iPulse]):
            print 'toto'
            noise = True
    globMean = np.mean(mean.values())
    globStdv = np.mean(stdv.values())

    # for iPulse in range(0, conf.nChannels):
    #     if mini[i] < (globMean - axisCutOff * globStdv) or maxi[i] > (globMean + axisCutOff * globStdv):
    #         noise[i] = True
    #         print axisCutOff * globStdv, globMean - axisCutOff * globStdv, globMean + axisCutOff * globStdv
    #         print 'Warning peak too high on channel {} : min/max = {}/{}'.format(i, mini[i], maxi[i])
    #     else:
    #         noise[i] = False

    for i in range(0, conf.nChannels):  # was 33
        # if i < 5: continue
        c.cd(i + 1)
        p = c.GetPad(i + 1)
        p.SetGrid()

        g = makePrettyGraph(x, y[i], ROOT.kRed)
        g1 = makePrettyGraph(x, newY[i], ROOT.kBlue)

        noise = False
        if noise is False:
            #  round to nearest hundred = avoid zooming too much
            g.SetMinimum(math.floor(min(mini.values()) / 100.0) * 100)
            g.SetMaximum(math.ceil(max(maxi.values()) / 100.0) * 100)
            print g.GetMinimum(), g.GetMaximum()
        else:
            g.SetMinimum(math.floor((globMean - axisCutOff * globStdv) / 100.0) * 100)
            g.SetMaximum(math.ceil((globMean + axisCutOff * globStdv) / 100.0) * 100)
            print g.GetMinimum(), g.GetMaximum(), axisCutOff, globMean, globStdv
        # miny = 0.9 * min(y[i])
        # maxy = 1.1 * max(y[i])
        # g.GetYaxis().SetRangeUser(miny, maxy)

        # g.GetXaxis().SetNdivisions(508)
        g.GetXaxis().SetLimits(400, 800)
        # g.GetXaxis().SetLimits(550, 650)

        # g.GetXaxis().SetLabelOffset(.1)
        # g.GetXaxis().SetLabelFont(43)

        g.Draw("ALX+")
        g1.Draw("L")
        graphs.append(g)
        graphs.append(g1)

        strip = i

        right = ROOT.TLatex()
        right.SetNDC()
        right.SetTextFont(43)
        right.SetTextSize(20)
        right.SetTextAlign(13)
        right.DrawLatex(.92, .6, "%d" % strip)

        p.Update()
        p.Modify()
        c.Update()

    ### General text on canvas
    c.cd(0)

    # topText RIGHT
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(20)
    right.SetTextAlign(33)
    right.DrawLatex(.95, .97, "%s, Event number: %d" % (header, count))

    # CMS flag
    #right.SetTextAlign(13)
    #right.DrawLatex(.05, .97,"#bf{CMS} #scale[0.7]{#it{Work in progress}}")

    c.Modify()
    c.Update()
    c.Print("%s_%d.pdf" % (fname, count))
    # raw_input('Nick')


def parseSingleHV(file, header, fname):

    fIn = ROOT.TFile(file, "READ")
    tree = fIn.Get('data')

    # Create the list of branches to read from fIn
    pulseBranchList = []
    for bName in ['pulse_ch' + str(iChan) for iChan in range(0, conf.nChannels)]:
        pulseBranchList.append(ROOT.vector('double')())
        fIn.data.SetBranchAddress(bName, pulseBranchList[-1])

    for event in tree:
        time = vector2list(fIn.time)

        pulses = {}
        for iChan in range(0, conf.nChannels):
            pulses[iChan] = vector2list(pulseBranchList[iChan])

        miny = 5000000
        maxy = -5000000
        for p in pulses:  # skip 15?

            if p == 15: continue

            if min(pulses[p]) < miny: miny = min(pulses[p])
            if max(pulses[p]) > maxy: maxy = max(pulses[p])
        makePlot(time, pulses, header, fname, event.evNum, .9 * miny, 1.1 * maxy)

    fIn.Close()


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

    for runid in runList:
        print 'runid: ', runid

        dir = conf.dataDir + str(runid) + '/'
        print "Analyze run %s" % runid
        assert os.path.exists(dir) is True, sys.exit('[ERROR]: Directory `{}` not found...exiting'.format(dir))

        for hvPoint in os.listdir(dir):  # loop over all HV
            try:
                assert hvPoint.isdigit()
            except AssertionError:
                print 'Warning - skipping folder "{}"'.format(hvPoint)
                continue
            HVdir = dir + hvPoint + '/'
            print "Running in dir %s" % HVdir

            header = "Scan ID: %d, HV: %sV" % (int(runid), hvPoint)
            fname = HVdir + "Scan%d_%s" % (int(runid), hvPoint)
            parseSingleHV(HVdir + str(hvPoint) + '.dqm.root', header, fname)
            # parseSingleHV(HVdir + str(hvPoint) + '.root', header, fname)


if __name__ == "__main__":
    main()
