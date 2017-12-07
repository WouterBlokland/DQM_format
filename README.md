# Code to convert digitizer/digital oscilloscope data files into ROOT format

Edit the `config_dqm.py` file with proper variables

Run as :

``` bash
python -m DQM.py config_dqm # Note the missing .py extension
```

If you want to overide the list of runs set in the configFile you can provide it on the command line with:

```bash
python -m DQM.py config_dqm run1 run2 ...
or
python -m DQM.py config_dqm [run1,run2,...]
```
