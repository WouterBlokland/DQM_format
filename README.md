# Code to convert digitizer/digital oscilloscope data files into ROOT format

## Need root (with py bindings(?)) to be installed and sourced before launching the scripts

Edit the `config_dqm.py` file with proper variables:
- `dataDir` : fullPath to your data directory
- `dataFileFormat` : fileFormat containing the raw digi data. default from  wavedump os `wave%d.txt`. Scripts excpect a `%d` variable in the name to be replaced by the chan number
- `runList` : List of run to analyse
- `nChannels` : Number of channels connected to the digitiser
- `headerSize` : Number of lines in the header of each event. Default from wavedump is `7`
- `recordLength` : Number of samples took in each event. Default is `1024` but can be adjusted in the WaveDump.txt config file. Check in the raw digi file if unsure.
- `sampling` : in `MS/s`, needed to convert recordTimeStamp in proper time unit. Default is `250` for the 4channels desktop digitiser
- `pulsePolarity` : polarity of input pulses. With RPCs most probably negative. Value is `-1` or `+1`
- `noiseLimit` : 35  # in stdv, any peak bigger will be obliterated
- `timeOverThresholdLimit` : 10  # in ns = min ToT for a peak to be considered a proper signal, Only used in the efficiency script.


## Script description:

- `DQM.py`: Translate raw digi files to root tuples.
- `EventDisplay.py`:
- `efficiency.py`:

``` bash
python -m [script.py] config_file # Note the missing .py extension for the config file
```

If you want to override the list of runs set in the configFile you can provide it on the command line with:

```bash
python -m [script.py] configFile run1 run2 ...
or
python -m [script.py] configFile [run1,run2,...]
```
