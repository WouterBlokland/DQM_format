#!/usr/bin/env python
#
# Ensure that a division will return a float
from __future__ import division
import ROOT
import sys
import copy
from array import array
import math
from random import randint
import os

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


# -------------------------------------------------- #
def vector2list(vec):
    ret = []
    for i in vec:
        ret.append(i)
    return ret


# -------------------------------------------------- #
def makePlot(x, y, header, fName, count, miny, maxy):
    c = ROOT.TCanvas("c", "c", 1200, 900)
    c.Divide(2, int(math.ceil(conf.nChannels / 2)), 0.001, 0.002)
    graphs = []  # needed to store the TGraphs.. cannot overwrite as ROOT needs them to plot

    # loop over all strips
    for i in range(0, conf.nChannels):  # was 33
        # if i < 5: continue
        c.cd(i + 1)
        p = c.GetPad(i + 1)
        p.SetGrid()

        g = copy.deepcopy(ROOT.TGraph(len(x), array('d', x), array('d', y[i])))

        g.SetMarkerStyle(20)
        g.SetMarkerSize(.4)
        g.SetLineWidth(1)
        g.SetLineColor(ROOT.kRed)
        g.SetMarkerColor(ROOT.kRed)

        g.GetYaxis().SetTitleFont(43)
        g.GetYaxis().SetTitleSize(12)
        g.GetYaxis().SetLabelFont(43)
        g.GetYaxis().SetLabelSize(10)
        g.GetYaxis().SetNdivisions(3)

        g.SetMinimum(min(x))
        g.SetMaximum(max(x))

        # miny = 0.9*min(y[i-1])
        # maxy = 1.1*max(y[i-1])
        g.GetYaxis().SetRangeUser(miny, maxy)

        # Set only x-axis labels on some plots..
        # if i == 3 or i == 4 or i == 31 or i == 32 or i == 17 or i == 18: g.GetXaxis().SetLabelSize(10)
        # else: g.GetXaxis().SetLabelSize(0)
        g.GetXaxis().SetLabelSize(10)
        if i == 0 or i == 1:
            g.GetXaxis().SetLabelSize(0)

        # g.GetXaxis().SetNdivisions(508)

        g.GetXaxis().SetLabelOffset(.1)
        g.GetXaxis().SetLabelFont(43)

        g.Draw("AL AXIS X+")
        graphs.append(g)

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

    # General text on canvas
    c.cd(0)

    # topText RIGHT
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(20)
    right.SetTextAlign(33)
    right.DrawLatex(.95, .97, "%s, Event number: %d" % (header, count))

    # CMS flag
    # right.SetTextAlign(13)
    # right.DrawLatex(.05, .97,"#bf{CMS} #scale[0.7]{#it{Work in progress}}")

    c.Modify()
    c.Print("%s_%d.pdf" % (fName, count))


# -------------------------------------------------- #
def getListOfPulseBranches(tree, nChan):
    '''
    Return list of nChan branches to read from the tree
    '''
    pulseBranchList = []
    for bName in ['pulse_ch' + str(iChan) for iChan in range(0, nChan)]:
        pulseBranchList.append(ROOT.vector('double')())
        tree.SetBranchAddress(bName, pulseBranchList[-1])
    return pulseBranchList


# -------------------------------------------------- #
def parseSingleHV(file, header, fName):
    fIn = ROOT.TFile(file, "READ")
    tree = fIn.Get('data')
    # Create the list of branches to read from fIn
    pulseBranchList = getListOfPulseBranches(tree, conf.nChannels)

    for event in tree:
        time = vector2list(fIn.time)

        pulses = {}
        for iChan in range(0, conf.nChannels):
            pulses[iChan] = vector2list(pulseBranchList[iChan])

        miny = 5000000
        maxy = -5000000
        for p in pulses:
            if min(pulses[p]) < miny:
                miny = min(pulses[p])
            if max(pulses[p]) > maxy:
                maxy = max(pulses[p])
        makePlot(time, pulses, header, fName, event.evNum, .9 * miny, 1.1 * maxy)

    fIn.Close()
