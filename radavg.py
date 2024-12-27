
import numpy as np


"""
Example use:

>>> # assume image, radius_of_each_pixel, mask, are all arrays w/same shape
>>> ra = RadialAveragar(radius_of_each_pixel, mask, n_bins=101)
>>> radial_average = ra(image)
>>> ra.bin_centers # will give e.g. x-axis in a plot

"""

class RadialAverager(object):

    def __init__(self, q_values, mask, n_bins=101):
        """
        Parameters
        ----------
        q_values : np.ndarray (float)
            For each pixel, this is the momentum transfer value of that pixel
        mask : np.ndarray (int)
            A boolean (int) saying if each pixel is masked or not
        n_bins : int
            The number of bins to employ. If `None` guesses a good value.
        """

        # Assigning properties
        self.q_values = q_values
        self.mask = mask
        self.n_bins = n_bins

        # Calculating the bin width based on the number of bins
        self.q_range = self.q_values.max() - self.q_values.min()
        self.bin_width = self.q_range / (float(n_bins))

        # Assigning each pixel to a bin
        self._bin_assignments = np.floor( np.abs(self.q_values - self.q_values*1e-10 - self.q_values.min()) \
                                    / self.bin_width ).astype(np.int32)
        # Normalization array for each bin
        self._normalization_array = (np.bincount( self._bin_assignments.flatten(), weights=self.mask.flatten() ) \
                                    + 1e-100).astype(float)

        # Check that the bin assignments are correct
        assert self.n_bins >= self._bin_assignments.max() + 1, 'incorrect bin assignments'
        # Truncate the normalization array to the number of bins
        self._normalization_array = self._normalization_array[:self.n_bins]

        return
    

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
            raise ValueError('`image` and `q_values` must have the same shape')
        if not (image.shape == self.mask.shape):
            raise ValueError('`image` and `mask` must have the same shape')

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
 
