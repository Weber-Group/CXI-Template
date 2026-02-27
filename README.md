# CXI-Template
Template fast-analysis code for CXI Experiments in standard configuration #2.
## Setup
Use this template to make a new repository, and don't forget to edit `config.yaml` file to match the experiment.

### To set up the environment that is needed for this code, run the following commands. Note: you do **not** need to `pip install` anything.
```bash
conda init
```
```bash
conda config --append envs_dirs /sdf/group/lcls/ds/tools/conda_envs/
```
```bash
conda activate weber_group
```
```bash
ipython kernel install --user --name=weber_group --display-name "weber-group"
```

This will:
1. Set up your shell so that conda works properly.
2. Tell conda to look for environments in `/sdf/group/lcls/ds/tools/conda_envs/`
3. Activate the `weber_group` environment
4. Make the `weber_group` environment avaliable as a Jupyter kernel, called `weber-group`.

### You may need to restart your OnDemand session in order for these changes to take affect.
Once everything is done, check if it worked by hitting the "New Launcher" `+` icon in the upper right hand corner. Under the tabs for "Notebook" and "Console", you should see new entries for using the `weber-group` environment. Once this is done, you shouldn't have to do this for future experiments.
<p align="center">
  <img width="492" height="472" alt="Image" src="https://github.com/user-attachments/assets/38691a95-f2af-4b21-b65f-6aef25b8e28f" />
</p>

#### Troubleshooting environment creation:
 - Ensure that `~/.bash_profile` exists, and contains the following commands:
 ```
 # Run the code in .bashrc
 if [ -f ~/.bashrc ]; then
        . ~/.bashrc
 fi
 ```
 - When executing code within a notebook, make sure you are using the `weber-group` kernel. In the upper right hand corner, you can change the kernel by clicking on the current kernel. There will be along list. Choose the one named `weber-group`.

# Standard experiment to-do list.
1. Set photon energy in producer, ADU cutoff to 2.5 
2. Take pedestal, dark, background, Ne, SF6 run. Background, Ne, or SF6 can be timetool calibration runs as well
3. Run masking notebook on the dark, background, and sample run
4. Run geometry calibration notebook on SF6 run, Add geometry calibration to producer
5. Run timetool calibration notebook.
6. Take sample run, run ADU notebook to determine sample ADU cutoff
7. Add sample ADU cutoff to producer
8. Re-process any sample runs with new producer settings
9. Run Compare_Runs notebook on dark, background, Ne, SF6, and sample for baseline measurements.
10. Run pump probe notebook on sample data.

### Notes
 - A pedestal is a dark run which is used to set specific detector parameters. Usually this is run once.
 - A dark run, but not a pedestal, is commonly used to mask pixels on the detector *after* the pedestal corrections.

# General Analysis workflow

For experiments following standard configuration #2, the data pipeline consists of two parts. Pre- and post-processing.

## Pre-processing
The raw data streams in from multiple sources into the DAq and saved into `.xtc` files. These files are typically very large, and too much to handle for analyzing multiple runs at once.

A pre-processing script, refered to as a "producer", is used to shrink the data down, applying light processing to acheive a more managable size.

During an experiment, there is typically only one section that must be edited in the producer, which are the azimuthal intergration parameters. The producer is found here `/sdf/data/lcls/ds/cxi/[EXPERIMENT]/results/smalldata_tools/lcls1_producers/smd_producer.py`

The function `getAzIntParams()`, returns a `dict` of kwargs based on the run number which are passed to the `AzimuthalIntegration` class. The photon energy, ADU cutoff (image threshold), q-binning, phi-binning,  and geometry calibration parameters are set here, typically for ranges of runs.

The producer will save specified data to an `.h5` file for each run. These files should be much smaller, and they exist here: `/sdf/data/lcls/ds/cxi/[EXPERIMENT]/hdf5/smalldata/`, unless otherwise specified by parameters passed to the producer.

### Notes
The Jungfrau-4M detector is sort-of energy resolved, so setting an image cutoff is a (very) crude way to remove unwanted background signal and sample fluorescence. To determine an appropriate ADU cutoff, use `ADU_Hist_plotter.ipynb`. This reads data directly from the `.xtc` files and builds a histogram of counts on the detector. You'll see a series of steps, the first peak should coencide with the photon energy. Any peaks before this, as long as they are low enough, can be removed by placing the ADU cutoff right above it. For instance, the ADU cutoff for SF6 is 2.5 keV.

## Post-processing
After the producer reduces the file size of the data, multiple runs can be processed within jupyter notebooks. There are template versions of these notebooks inside this repository for specific analysis tasks, such as the geometry calibration process, masking, and pump-probe plotting. See the index section below for more information, and see inside the notebooks for notebook-specific information.

# Index

#### `ADU_Hist_Plotter.ipynb`
Used for determining ADU cutoffs for sample runs. Useful for determining fluorescence contribution to signal.

#### `Compare_Runs.ipynb`
This notebook saves the average of azimuthal averages for a run into a folder. This notebook is useful for comparing scattering between runs.

#### `Geometry_Calibration.ipynb`
Used for determining the x,y-center of the primary beam on the Jungfrau-4M as well as the cell-detector distance. These parameters are needed for proper azimuthal integration and the transform to momentum space. There are many methods in which the calibration can be done but this method fits a high-level ground state *ab initio* scattering pattern of a sample, typically SF6 to determine these parameters.

#### `Knife_Edge.ipynb`
This notebook is used typically on a knife-edge scan, which is used to determine the focal parameters of the laser. This notebook takes that data, filteres it, and fits it to an erf.

#### `Mask_Maker.ipynb`
This notebook combines three types of runs, along with pre-defined masks to generate a combined mask (`cmask`), which is then saved to a specific directory so that it is applied in the data stream. More details inside the notebook.

#### `Pump_Probe.ipynb`
This notebook is the main data plotter, once everything has been calibrated and is working corretly. It takes pump-probe runs, filteres the data, re-bins the time points and plots the percent difference signal, plus q- and t-lineouts.

#### `Timetool_Calibration.ipynb`
Used on a timetool calibration run to determine the timetool calibration parametes. Optionally, save this data directly to the `config.yaml`.

#### `config.yaml`
To keep things clean, these notebooks pull data from `config.yaml`, which can specify general information about an experiment, such as the experiment number, data paths, photon energy, and run type. I much prefer this method as changing things across multiple notebooks can be annoying.