# DICE-like models in Python

This is a little application put together by Kyle Duffy to run simulations for integrated assessment models (IAMs) derived from DICE (Nordhaus et al. 2016). The current version suffers some optimization issues due to high dimensionality and weaknesses of `scipy.optimize`, but simulation is currently functional and the code supports SICE models (Ikefuji et al. 2019) and a SICE variant where temperature dynamics from Golosav et al. are substituted in place of those from Ikefuji et al. Really, any number of additional variants could easily be added by the determined user.

## Setup and usage instructions

At the moment this project depends on `numpy`, `pandas`, and `scipy`, but I've put together a little script so you don't have to configure everything yourself. To use the code, first make sure you have [Python 3 installed](https://www.python.org/downloads/). Any version of Python 3 should work, but I recommend using the most recent version, which is 3.9.4 at the time of writing. (Or better yet, use [pyenv](https://github.com/pyenv/pyenv) to manage your versions of Python).

Once Python 3 is installed, you can run
```
python configure_python.py
```
in your command line environment (e.g. Terminal on mac). Note that if you're on Mac, Python 2 comes preinstalled out of the box. To make sure you're using Python 3, you can run 
```
python3 configure_python.py
```
instead.

If you're on Windows, open PowerShell as an **administrator** (it's important you're in adminstrator mode) and run
```
python.exe configure_python.py
```

If your configuration was successful, you'll get a confirmation and it will tell you how to activate the newly created virtual environment. Once you've done that (you should see the name of the virtual environment appear in parentheses before your prompt, e.g. `(DICE)`), you can interact with the code using the `solver.py` module. To get a help message, run
```
python solver.py -h
```
on Mac and Linux or
```
python.exe solver.py -h
```
on Windows.

Follow the usage instructions and run as many simulations as you want! To change the parameters, you can edit the default values in `specs.py`. To get the original version, just re-download the original file form this repository. (This is pretty clunky, but I don't currently have the time to wrap this up with a better UX)