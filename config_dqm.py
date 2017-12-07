# Path to digitiser data folder, root file will also be written here
# Script expect the txt files in folder with HV value
dataDir = "/home/webdcs/webdcs/HVSCAN/%s/"
dataFileFormat = 'wave%d.txt'
runList = [0]  # List of run to convert
nChannels = 4  # Channels connected on the digitiser
headerSize = 7  # Number of lines in the header
recordLength = 1024  # Number of sample took in each event
