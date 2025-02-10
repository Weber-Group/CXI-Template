import matplotlib.pyplot as plt
import numpy as np
import h5py
from typing import List, Dict, Union

"""
This file contains utilities for performing radial averaging on image data, 
exploring HDF5 file structures, and visualizing detector data.

Classes:
    RadialAverager: Performs radial averaging on 2D data.

Functions:
    get_tree(f): Lists the full tree of an HDF5 file.
    is_leaf(dataset): Checks if an HDF5 node is a dataset.
    get_leaves(f, saveto, verbose=False): Extracts datasets from an HDF5 file.
    runNumToString(num): Converts a number to a zero-padded string.
    plot_jungfrau(x, y, f, ax=None, shading='nearest', *args, **kwargs): Plots Jungfrau detector counts.
"""
class RadialAverager(object):

    def __init__(self, q_values, mask, n_bins=101):
        """
        Parameters
        ----------
        q_values : np.ndarray (float)
            For each pixel, this is the momentum transfer value of that pixel.
        mask : np.ndarray (int)
            A boolean (int) array indicating if each pixel is masked (1) or not (0).
        n_bins : int
            The number of bins to employ.
        """

        self.q_values = q_values
        self.mask = mask
        self.n_bins = n_bins

        # Calculate bin width and range
        self.q_range = self.q_values.max() - self.q_values.min()
        self.bin_width = self.q_range / float(n_bins)

        # Assign each pixel to a bin
        self._bin_assignments = np.floor(
            (self.q_values - self.q_values.min()) / self.bin_width
        ).astype(np.int32)

        # Ensure bin assignments fit within the number of bins
        assert self.n_bins >= self._bin_assignments.max() + 1, 'Incorrect bin assignments'

        # Normalization array for each bin
        self._normalization_array = (
            np.bincount(self._bin_assignments.flatten(), weights=self.mask.flatten()) + 1e-100
        ).astype(float)
        self._normalization_array = self._normalization_array[:self.n_bins]
    

    def __call__(self, image):
        """
        Bin pixel intensities by their momentum transfer.
        
        Parameters
        ----------            
        image : np.ndarray
            The intensity at each pixel, same shape as pixel_pos
        Returns
        -------
        bin_centers : ndarray, float
            The q center of each bin.
        bin_values : ndarray, int
            The average intensity in the bin.
        """
        # Check that the image and q_values have the same shape
        if not (image.shape == self.q_values.shape):
            raise ValueError('image and q_values must have the same shape')
        if not (image.shape == self.mask.shape):
            raise ValueError('image and mask must have the same shape')

        # Calculate the weighted average of the image in each bin
        weights = image.flatten() * self.mask.flatten()
        bin_values = np.bincount(self._bin_assignments.flatten(), weights=weights)
        # 
        bin_values /= self._normalization_array

        # Check that the bin values have the correct shape
        assert bin_values.shape[0] == self.n_bins

        return bin_values
    

    @property
    def bin_centers(self):
        return (np.arange(self.n_bins) + 0.5) * self.bin_width + self.q_values.min()

    @property
    def pixel_counts(self):
        return self._normalization_array


def plot_jungfrau(x, y, f, ax=None, shading='nearest', *args, **kwargs):
    """Plot Jungfrau detector counts.

    Parameters
    ----------
    x, y : list of np.ndarray
        Coordinates for each tile of the detector.
    f : list of np.ndarray
        Data to be plotted for each tile.
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, uses current axes.
    shading : str, optional
        Shading style for pcolormesh (default: 'nearest').

    Returns
    -------
    pcm : matplotlib.collections.QuadMesh
        The QuadMesh object created.
    """
    if ax is None:
        ax = plt.gca()
    for i in range(8):
        pcm = ax.pcolormesh(x[i], y[i], f[i], shading=shading, *args, **kwargs)
    return pcm

def combineRuns(runNumbers, folder, keys_to_combine, keys_to_sum, keys_to_check, verbose=False):
    """Combine data from multiple runs into a single dataset.

    Parameters
    ----------
    runNumbers : list of int
        List of run numbers to combine.
    folder : str
        Path to the folder containing the data files.
    verbose : bool, optional
        If True, print detailed information during processing (default: False).

    Returns
    -------
    data_combined : dict
        Dictionary containing combined data from all runs.
    """
    data_array = []
    experiment = folder.split('/')[6]
    for i,runNumber in enumerate(runNumbers):
        data = {}
        filename = f'{folder}{experiment}_Run{runNumToString(runNumber)}.h5'
        print('Loading: ' + filename)
        with h5py.File(filename,'r') as f:
            get_leaves(f,data,verbose=verbose)
            data_array.append(data)
    data_combined = {}
    for key in keys_to_combine:
        arr = np.squeeze(data_array[0][key])
        for data in data_array[1:]:
            arr = np.concatenate((arr,np.squeeze(data[key])),axis=0)
        data_combined[key] = arr
    run_indicator = np.array([])
    for i,runNumber in enumerate(runNumbers):
        run_indicator = np.concatenate((run_indicator,runNumber*np.ones_like(data_array[i]['lightStatus/xray'])))
    data_combined['run_indicator'] = run_indicator
    for key in keys_to_sum:
        arr = np.zeros_like(data_array[0][key])
        for data in data_array:
            arr += data[key]
        data_combined[key] = arr
    for key in keys_to_check:
        arr = data_array[0][key]
        for i,data in enumerate(data_array):
            if not np.array_equal(data[key],arr):
                print(f'Problem with key {key} in run {runNumbers[i]}')
        data_combined[key] = arr
    print('Loaded Data')
    return data_combined

def get_tree(f):
    """List the full tree of the HDF5 file.

    Parameters
    ----------
    f : h5py.File
        The HDF5 file object to traverse.

    Returns
    -------
    None
        Prints the structure of the HDF5 file.
    """
    def printname(name):
        print(name, type(f[name]))
    f.visit(printname)
    
def is_leaf(dataset):
    """Check if an HDF5 node is a dataset (leaf node).

    Parameters
    ----------
    dataset : h5py.Dataset or h5py.Group
        The HDF5 node to check.

    Returns
    -------
    bool
        True if the node is a dataset, False otherwise.
    """
    return isinstance(dataset, h5py.Dataset)

def get_leaves(f, saveto, verbose=False):
    """Retrieve all leaf datasets from an HDF5 file and save them to a dictionary.

    Parameters
    ----------
    f : h5py.File
        The HDF5 file object to traverse.
    saveto : dict
        Dictionary to store the retrieved datasets.
    verbose : bool, optional
        If True, print detailed information about each dataset (default: False).

    Returns
    -------
    None
        The datasets are stored in the provided dictionary.
    """
    def return_leaf(name):
        if is_leaf(f[name]):
            if verbose:
                print(name, f[name][()].shape)
            saveto[name] = f[name][()]
    f.visit(return_leaf)

def runNumToString(num):
    """Convert a run number to a zero-padded string of length 4.

    Parameters
    ----------
    num : int
        The run number to convert.

    Returns
    -------
    numstr : str
        The zero-padded string representation of the run number.
    """
    numstr = str(num)
    while len(numstr) < 4:
        numstr = '0' + numstr
    return numstr