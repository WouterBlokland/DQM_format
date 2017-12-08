import ROOT
import sys
import copy
from array import array
import math
from random import randint
import os

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

time = None


def vector2list(vec):

    ret = []
    for i in vec:
        ret.append(i)
    return ret


def makePlot(x, y, header, fname, count, miny, maxy):

    c = ROOT.TCanvas("c", "c", 1200, 900)
    c.Divide(2, 9, 0.001, 0.002)
    graphs = []  # needed to store the TGraphs.. cannot overwrite as ROOT needs them to plot

    # loop over all strips
    for i in range(1, 17):  # was 33
        if i < 5: continue
        c.cd(i + 2)
        p = c.GetPad(i + 2)
        p.SetGrid()

        g = copy.deepcopy(ROOT.TGraph(len(x), array('d', x), array('d', y[i - 1])))

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

        #miny = 0.9*min(y[i-1])
        #maxy = 1.1*max(y[i-1])
        g.GetYaxis().SetRangeUser(miny, maxy)

        # Set only x-axis labels on some plots..
        #if i == 3 or i == 4 or i == 31 or i == 32 or i == 17 or i == 18: g.GetXaxis().SetLabelSize(10)
        #else: g.GetXaxis().SetLabelSize(0)
        g.GetXaxis().SetLabelSize(10)
        if i == 1 or i == 2: g.GetXaxis().SetLabelSize(0)

        #g.GetXaxis().SetNdivisions(508)

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

    ### General text on canvas
    c.cd(0)

    # topText RIGHT
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(20)
    right.SetTextAlign(33)
    right.DrawLatex(.95, .97, "%s, Event number: %06d" % (header, i))

    # CMS flag
    #right.SetTextAlign(13)
    #right.DrawLatex(.05, .97,"#bf{CMS} #scale[0.7]{#it{Work in progress}}")

    c.Modify()
    c.Print("/Users/croskas/PhD/RPC/Testbeam/Result_plots/%s_%d.pdf" % (fname, count))
    #c.Print("/Users/croskas/PhD/RPC/Testbeam/Result_plots/%s_%d.png" % (fname, count))


def parseSingleHV(file, header, fname):

    fIn = ROOT.TFile(file, "READ")
    t = fIn.Get("data")
    time = fIn.Get("time")

    for i in range(0, t.GetEntries() + 1):

        time = vector2list(time)

        t.GetEntry(i)

        pulses = {}
        pulses[0] = vector2list(t.pulse_ch0)
        pulses[1] = vector2list(t.pulse_ch1)
        pulses[2] = vector2list(t.pulse_ch2)
        pulses[3] = vector2list(t.pulse_ch3)
        pulses[4] = vector2list(t.pulse_ch4)
        pulses[5] = vector2list(t.pulse_ch5)
        pulses[6] = vector2list(t.pulse_ch6)
        pulses[7] = vector2list(t.pulse_ch7)
        pulses[8] = vector2list(t.pulse_ch8)
        pulses[9] = vector2list(t.pulse_ch9)
        pulses[10] = vector2list(t.pulse_ch10)
        pulses[11] = vector2list(t.pulse_ch11)
        pulses[12] = vector2list(t.pulse_ch12)
        pulses[13] = vector2list(t.pulse_ch13)
        pulses[14] = vector2list(t.pulse_ch14)
        pulses[15] = vector2list(t.pulse_ch15)

        miny = 5000000
        maxy = -5000000
        for p in pulses:  # skip 15?

            if p == 15: continue

            if min(pulses[p]) < miny: miny = min(pulses[p])
            if max(pulses[p]) > maxy: maxy = max(pulses[p])

        makePlot(time, pulses, header, fname, i, .9 * miny, 1.1 * maxy)

    fIn.Close()


if __name__ == "__main__":

    runid = 000002
    runid = "%06d" % runid

    #dir = "/home/webdcs/webdcs/HVSCAN/%06d/" % runid
    dir = "/Users/croskas/PhD/RPC/Testbeam/ROOT_files/"
    print "Analyze run %s" % runid

    #wwwbase = "/var/www/html/HVSCAN/%06d/" % runid
    #if not os.path.exists(wwwbase): os.makedirs(wwwbase)

    for x in os.listdir(dir):  # loop over all HV

        header = "Scan ID: %06d, %s" % (int(runid), x)
        fname = "Scan%06d_%s" % (int(runid), x)

        #www = wwwbase + x
        #if not os.path.exists(www): os.makedirs(www)

        HVdir = dir + x
        file = dir + "/" + x  #+ ".dqm.root"

        parseSingleHV(file, header, fname)
