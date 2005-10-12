"""
Histogram

$Id:
"""

# CEB:
# This file is still being written.

# These imports are required only for the extra statistical functions (e.g. vector sum);
# they are not required to have a histogram.
from math import pi
from Numeric import innerproduct, array, exp
from utils import arg


# To do:
#
# - come up with a name
# - use one dictionary with a two-valued list for each dictionary value: (value, counts). This
#   will allow counts(), values(), and bins() to come out in the same order.
# - function to return value in a range (like a real histogram)
# - cache values
# - check use of float() in count_mag() etc
# - assumes cyclic axes start at 0: include a shift based on range




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
        self.data = {}
        self._counts = {}
        
        self.total_count = 0
        self.total_value = 0.0

        self.undefined_vals = 0 

        self.axis_bounds = axis_bounds
        self.axis_range = axis_bounds[1] - axis_bounds[0]
        self.cyclic = cyclic        


    def get(self, bin):
        """
        Return the value of bin.
        """
        return self.data.get(bin)


    def num_bins(self):
        """
        Return the number of bins.
        """
        return len(self.data)


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
                # ignore this bin if it's outside the range because this isn't a cyclic hist.
                if not (self.axis_bounds[0] <= bin <= self.axis_bounds[1]):
                    #raise OperandRangeError
                    continue
                
            if bin not in self.data:
                self.data.update({bin: 0.0})
                self._counts.update({bin: 0})

            new_value = new_data.get(bin)  
            self.total_value += new_value
            self._counts[bin] += 1
            self.total_count += 1

            if keep_peak == False:
                self.data[bin] += new_value
            else:
                if new_value > self.data[bin]: self.data[bin]=new_value


    def weighted_sum(self):
        """
        Return the sum of each value times its bin 
        """
        return innerproduct(self.data.keys(), self.data.values()) 


    def weighted_average(self):
        """
        Return the average value of data along the bin-axis; each bin is
        weighted by its value.

        This quantity is a continuous
        measure of the max_value_bin() of the distribution for a
        non-cyclic distribution, i.e.  one with distinct upper and lower
        bounds.
        """
        return self._safe_divide(self.weighted_sum(),sum(self.data.values()))   # ?


    def vector_sum(self):
        """
        Return the vector sum of the data as the 2-tuple (magnitude, direction).

        ** direction is maybe a bad name
        ** The returned direction has the same dimensions as the bin_axis specified on creating the binogram.

        Each bin contributes a vector of length equal to its value, at a direction
        of the bin itself (scaled to [0,2pi] according to the range specified on creating the binogram).


        Magnitude:
        
        
        Direction:
        This quantity is a continuous measure of the
        max_value_bin() of the distribution, assuming the distribution is
        cyclic i.e. wraps around from the top of axis_bounds to the bottom (e.g.
        direction, where 0 = 2pi radians).

        It has more precision than the bin_number of the peak (i.e.
        bin_mag(max_value_bin())) because it is computed from the entire
        distribution instead of just the bin_number of the peak bin.

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

        r = self.data.values()                                  
        theta = self._bins_to_radians(array(self.data.keys()))
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
        return self._safe_divide(self.vector_sum()[0], len(self.data))


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
        return self._safe_divide(self.vector_mag(), sum(self.values()))


# where should comment about these go?
#        The sum of the current counts: sum(self.counts.values())
#        The sum of the current values.
#        return max(self.data.values())
#        return min(self.data.values())
#        return max(self.counts.values())
#        return min(self.counts.values())


    def values(self):
        """
        """
        return self.data.values()


    def bins(self):
        """
        """
        return self.data.keys()
    
    
    def counts(self):
        """
        """
        return self._counts.values()


# fix this
    def max_value_bin(self):
        """
        The bin with the largest value.
        """
        return argmax(self.data.values()) #?????


    def value_mag(self, bin):
        """
        Return the value of a single bin in the histogram as a portion of total_value.
        """
        return self._safe_divide(self.data.get(bin), self.total_value)


    def count_mag(self, bin):
        """
        Return the count of a single bin in the histogram as a portion of total_count.
        """
        return self._safe_divide(float(self._counts.get(bin)), float(self.total_count)) # use of float()


    # not tested
    def relative_value(self, bin):
        """
        Return the value of the given bin as a proportion of the
        sum_value().

        This quantity is on a scale from 0.0 (the
        specified bin is zero and others are nonzero) to 1.0 (the
        specified bin is the only nonzero bin).  If the histogram is
        empty the result is undefined; in such a case zero is returned
        and the value returned by undefined_values() is incremented.
        """
        return self._safe_divide(self.data.get(bin), sum(self.values()))


    # not tested
    def relative_selectivity(self):
        """
        Return value(max_value_bin()) as a proportion of the
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
        ## With only one bin, one is always fully selective; special
        ## case to avoid divide-by-zero errors. 
        if len(self) <= 1:  # that's not going to work
            return 1.0

        proportion = _safe_divide(max_value_bin(), sum(self.values()))
        offset = 1.0/len(self)
        scaled = (proportion-offset)/(1.0-offset)
        return scaled  # miss assumption about +ve


    def _bins_to_radians(self, bins):
        return (2*pi)*bins/self.axis_range


    def _radians_to_bins(self, angles):
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

        



    
