"""
Histogram

$Id:
"""

# CEB:
# This file is still being written.
#
# To do:
#
# - come up with a name...it records a distribution of values and
#   lets you get some statistics on it
# - complete the documentation
# - raise OperandRangeError, or whatever, in add()
# - relative selectivity
# - check use of float() in count_mag() etc
#
# - function to return value in a range (like a real histogram)
# - cache values
# - assumes cyclic axes start at 0: include a shift based on range
#
# - is there a way to make this work for arrays without mentioning
#   "array" anywhere in here?
# - should this be two classes: one for the core (which would be
#   small though) and another for statistics?





# These imports are required only for the extra statistical functions (e.g. vector sum);
# they are not used for anything else.
from math import pi
from Numeric import innerproduct, array, exp, argmax
from utils import arg


class Distribution(object):

    """
    Distribution
    Histogram-like object that is a dictionary of bins:values. Each
    bin's value is the sum of all values that have been placed into
    it.

    The bin-axis is continuous, and can represent a physical quantity
    (such as direction or frequency).

    A bin is placed along this axis whenever one is specified by input
    data, and its value is set equal to the one specified (unless the
    bin has previously been created, in which case its value is added
    to).

    ** The range that the bins may fall in is specified by the
    axis_bounds; any input data with a bin outside are ignored unless
    cyclic=True, in which case they are allowed and later wrapped
    according to axis_bounds (upper limit=lower limit, e.g. 0 = 2*pi)
    in any calculations. So for non-cyclic data the bounds are just
    used to check input but for cyclic data they affect the
    calculation of vector quantities**

    Also contains a dictionary, _counts, which stores bins:counts. Each
    bin's count is the number of times that a value has been added to
    the bin (the value could have been zero).

    In addition, stores the total value that has been added to the
    object, and the total count of times a value was added.

    ** This object is designed to include some features that are not
    strictly speaking part of histograms ... e.g. if their total
    counts are less than the sum of the individual counts, or if
    individual counts are less than zero.
    """

    def __init__(self, axis_bounds=(0.0, 2*pi), cyclic=False):
        """
        ** ..
        
        total_count holds the total number of values that have ever been provided for each
        bin.  ** For a simple histogram this will be the same as
        sum_counts(), but for other OneDBinList types it often
        differs. 

        total_value holds the sum of all of the values ever provided for each bin.  ** For a
        simple histogram this will be the same as sum_value(), but for
        other OneDBinList types it often differs from sum_value().

        undefined_vals holds the number of times that undefined values have been
        returned from calculations for ** any instance of this class,
        e.g. calls to vector_direction() or vector_selectivity() when no
        value is non-zero.  Useful for warning users when the values are
        not meaningful.
        """
        self._data = {}
        self._counts = {}
        
        self.total_count = 0
        self.total_value = 0.0

        self.undefined_vals = 0 

        self.axis_bounds = axis_bounds
        self.axis_range = axis_bounds[1] - axis_bounds[0]
        self.cyclic = cyclic        


    def get_value(self, bin):
        """
        Return the value of bin.
        """
        return self._data.get(bin)


    def get_count(self, bin):
        """
        Return the count of bin.
        """
        return self._counts.get(bin)
    
        
    def values(self):
        """
        Return a list of (bin, value) pairs, as 2-tuples.

        Get a list of values with e.g.: [value for bin,value in dist1.values()]

        Where should the following note go (see also get_counts())?
        Various statistics could be calculated from these values. For
        example, the sum of the current values,
        the largest value of any bin, ...
        any bin, 
        """
        return self._data.items()


    def counts(self):
        """
        Return a list of (bin, count) pairs, as 2-tuples.        

        e.g. use to get
        The sum of the current counts, the largest count of any bin, ...
        """
        return self._counts.items()


    def num_bins(self):
        """
        Return the number of bins.
        """
        return len(self._data)


    def add(self, new_data, keep_peak=False):
        """
        Add new data in the form of a dictionary: {bin, value}.
        If the bin already exists, the value is added to its current value.
        If the bin doesn't exist, it is created with that value.

        If bin is outside axis_bounds, its position is allowed for cyclic=True and ignored
        for cyclic=False. 

        If keep_peak=True, value becomes the new value for that bin if it's value
        is greater than the bin's current value. 
        Useful for maintaining a
        distribution of maxiumum values for different bins, as opposed
        to the summations typical to histogram bins.  Note that each
        call will increase the total_value and total_count (and thus
        decrease the value_mag() and count_mag()) even if the value
        doesn't happen to be the maximum seen so far, since each data
        point still helps improve the sampling and thus the confidence.
        """
        for bin in new_data.keys():

            if self.cyclic==False:
                # Raise an error if this bin is outside the range because this isn't a cyclic distribution.
                if not (self.axis_bounds[0] <= bin <= self.axis_bounds[1]):
#                    raise SomethingError("Bin outside bounds (this will be OperandRangeError or something).")
                     continue #remove once you implement error above
                 
            if bin not in self._data:
                self._data.update({bin: 0.0})
                self._counts.update({bin: 0})

            new_value = new_data.get(bin)  
            self.total_value += new_value
            self._counts[bin] += 1
            self.total_count += 1

            if keep_peak == False:
                self._data[bin] += new_value
            else:
                if new_value > self._data[bin]: self._data[bin]=new_value


    def max_value_bin(self):
        """
        Return the bin with the largest value.
        """
        return self._data.keys()[argmax(self._data.values())]


    def weighted_sum(self):
        """
        Return the sum of each value times its bin 
        """
        return innerproduct(self._data.keys(), self._data.values()) 


    def weighted_average(self):
        """
        Return the average of the data on the bin_axis, where each bin is
        weighted by its value.

        This quantity is a continuous
        measure of the bin with the largest value - for a
        non-cyclic distribution, i.e.  one with distinct upper and lower
        bounds.
        """
        return self._safe_divide(self.weighted_sum(),sum(self._data.values())) 


    def vector_sum(self):
        """
        Return the vector sum of the data as the 2-tuple (magnitude, direction).

        ** direction is maybe a bad name
        ** since returned direction has the same dimensions as the bin_axis specified on creating the binogram.

        Each bin contributes a vector of length equal to its value, at a direction
        of the bin itself (scaled to [0,2pi] according to the range specified on creating the binogram).
        
        The direction is a continuous measure of the
        max_value_bin() of the distribution, assuming the distribution is
        cyclic i.e. wraps around from the top of axis_bounds to the bottom (e.g.
        direction, where 0 = 2pi radians).

        It has more precision than finding the bin with the largest value
        (i.e. max_value_bin()) because it is computed from the entire
        distribution instead of just the peak bin.

        no longer
        ** However, it requires uniform sampling for correct results, which
        ** is not always possible.

        The direction is not meaningful when
        the magnitude is 0, since a zero-length vector has no
        direction.  To find out whether such cases occurred, you can
        compare the value of undefined_vals before and after
        a series of calls to this function.

        If cyclic=false, might want to warn this was not the thing to do?
        """
        # vectors are represented in polar form as complex numbers

        r = self._data.values()                                  
        theta = self._bins_to_radians(array(self._data.keys()))
        v_sum = innerproduct(r, exp(theta*1j))                  

        magnitude = abs(v_sum)
        direction = arg(v_sum)

        if v_sum == 0:
            self.undefined_vals += 1
        
        return (magnitude, self._radians_to_bins(direction)) 


    def vector_average(self):
        """
        ** Return 
        i.e. the vector sum divided by the number of bins.
        """
        return self._safe_divide(self.vector_sum()[0], len(self._data))


    # not tested
    def relative_selectivity(self):
        """
        Return valuemax_value_bin()) as a proportion of the
        sum_value(), scaled to 0.0 to 1.0.

        This quantity is a measure of how strongly the histogram is
        biased towards the
        max_value_bin().  For a smooth, single-lobed distribution with an
        inclusive, non-cyclic range, this quantity is an analog to
        vector_selectivity.  To be a precise analog for arbitrary
        distributions, it would need to compute some measure of the
        selectivity that works like the weighted_average() instead of
        the max_value_bin().  The scaling is such that if all bins are
        identical, the selectivity is 0.0, and if all bins but one are
        zero, the selectivity is 1.0.      
        """
        # With only one bin, one is always fully selective
        if len(self._data) <= 1: 
            return 1.0

        proportion = self._safe_divide(self._data[self.max_value_bin()], sum(self._data.values()))
        offset = 1.0/len(self._data)
        scaled = (proportion-offset)/(1.0-offset)

        # "Since we take the peak, negative selectivities shouldn't be possible, but just in case..."
        # So make this Number(bounds=(0.0, 1.0)) and use set_in_bounds() or something?
        return scaled 


    # not tested
    def vector_selectivity(self):
        """
        Returns the ratio of the length of the vector sum to the sum of the vector lengths
        i.e. vector_mag()/sum_value()

        This is a vector-based measure of the peakedness of the histogram.
        If only a single bin has a non-zero value(), the selectivity
        will be 1.0, and if all bins have the same value() then the
        selectivity will be 0.0.  Other distributions will result in
        intermediate values.

        For a histogram with a sum_value() of zero (i.e. all bins
        empty), the selectivity is undefined.  Assuming that one will
        usually be looking for high selectivity, we return zero in such
        a case so that high selectivity will not mistakenly be claimed.
        To find out whether such cases occurred, you can compare the
        value of undefined_values() before and after a series of
        calls to this function.
        """
        return self._safe_divide(self.vector_sum()[0], sum(self._data.values()))


    def value_mag(self, bin):
        """
        Return the value of a single bin in the histogram as a portion of total_value.
        """
        return self._safe_divide(self._data.get(bin), self.total_value)


    def count_mag(self, bin):
        """
        Return the count of a single bin in the histogram as a portion of total_count.
        """
        return self._safe_divide(float(self._counts.get(bin)), float(self.total_count)) # use of float()


    def _bins_to_radians(self, bins):
        """
        Based on the axis_range given on creation of this distribution, take 
        """
        # assumes bins is a Numeric array
        return (2*pi)*bins/self.axis_range 


    def _radians_to_bins(self, angles):
        """
        """
        # assumes angles is a Numeric array
        return angles*self.axis_range/(2*pi)
        
        
    def _safe_divide(self,numerator,denominator):
        """
        Division routine that avoids division-by-zero errors
        (returning zero in such cases) but keeps track of them
        for undefined_values.
        """
        if denominator==0:
            self.undefined_vals += 1
            return 0  # should that return a float? or the same type as numerator?
        else:
            return numerator/denominator


##    # not tested - not used by anyone?
##
##    def relative_value(self, bin):
##        """
##        Return the value of the given bin as a proportion of the
##        sum_value().
##
##        This quantity is on a scale from 0.0 (the
##        specified bin is zero and others are nonzero) to 1.0 (the
##        specified bin is the only nonzero bin).  If the histogram is
##        empty the result is undefined; in such a case zero is returned
##        and the value returned by undefined_values() is incremented.
##        """
##        return self._safe_divide(self._data.get(bin), sum(self.values()))





        



    
