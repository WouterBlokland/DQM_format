# Path to digitiser data folder, root file will also be written here
# Script expect the txt files in folder with HV value
# dataDir = "/home/webdcs/webdcs/HVSCAN/%s/"
# dataDir = "/eos/user/a/apingaul/RPCRND/Data/Digitiser/"
dataDir = "/eos/user/a/apingaul/RPCRND/Data/Digitiser/delayLossTest/pmt2_1.4kV/"
dataFileFormat = 'wave%d.txt'
runList = [0]  # List of run to convert
normalChan = [0, 1]
delayChan = [3]
totalChan = [2]
nChannels = 4  # Channels connected on the digitiser
headerSize = 7  # Number of lines in the header
recordLength = 1024  # Number of sample took in each event
sampling = 250  #MS/s, needed to convert recordTimeStamp in us

# pulsePolarity used to look for neg/pos signal to compute the efficiency.
pulsePolarity = -1  # -1 = Negative, 1 = Positive
timeOverThresholdLimit = 10 # in ns = minTot for a signal
noiseLimit = 30 # in stdv, any peak bigger will be obliterated
