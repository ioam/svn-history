"""
Distribution class

$Id$
"""

# To do:
#
# - test selectivity()
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



# The basic functions do not have any dependencies, but these imports
# are needed for some of the statistical functions (e.g. vector sum).
from math import pi
from Numeric import innerproduct, array, exp, argmax
from utils import arg


class Distribution(object):
    """
    Holds a distribution of the values f(x) associated with a variable x.
    
    A Distribution is a histogram-like object that is a dictionary of
    samples.  Each sample is an x:f(x) pair, where x is called the bin
    and f(x) is called the value(). Each bin's value is typically
    maintained as the sum of all the values that have been placed into
    it.

    The bin axis is continuous, and can represent a continuous
    quantity without discretization.  Alternatively, this class can be
    used as a traditional histogram by either discretizing the bin
    number before adding each sample, or by binning the values in the
    final Distribution.

    Distributions are bounded by the specified axis_bounds, and can
    either be cyclic (like directions or hues) or non-cyclic.  For
    cyclic distributions, samples provided outside the axis_bounds
    will be wrapped back into the bound range, as is appropriate for
    quantities like directions.  For non-cyclic distributions,
    providing samples outside the axis_bounds will result in a
    ValueError.

    In addition to the values, can also return the counts, i.e., the
    number of times that a sample has been added with the given bin.

    Not all instances of this class will be a true distribution in the
    mathematical sense; e.g. the values will have to be normalized
    before they can be considered a probability distribution.

    If keep_peak=True, the value stored in each bin will be the
    maximum of all values ever added, instead of the sum.  The
    distribution will thus be a record of the maximum value
    seen at each bin, also known as an envelope.
    """

    # Holds the number of times that undefined values have been
    # returned from calculations for any instance of this class,
    # e.g. calls to vector_direction() or vector_selectivity() when no
    # value is non-zero.  Useful for warning users when the values are
    # not meaningful.
    undefined_vals = 0 

    def __init__(self, axis_bounds=(0.0, 2*pi), cyclic=False, keep_peak=False):
        self._data = {}
        self._counts = {}
            
        # total_count and total_value hold the total number and sum
        # (respectively) of values that have ever been provided for
        # each bin.  For a simple distribution these will be the same as
        # sum_counts() and sum_values().
        self.total_count = 0
        self.total_value = 0.0
        
        self.axis_bounds = axis_bounds
        self.axis_range = axis_bounds[1] - axis_bounds[0]
        self.cyclic = cyclic
        self.keep_peak = keep_peak


    def get_value(self, bin):
        """Return the value of the specified bin."""
        return self._data.get(bin)


    def get_count(self, bin):
        """Return the count from the specified bin."""
        return self._counts.get(bin)
    

    ### JABALERT!
    ### 
    ### Seems to me that it would make the user's life easier if we
    ### went ahead and provided the two separate lists, i.e.  bins()
    ### and values(), to simplify all of their expressions.  Sure,
    ### they can do it with the tuple list using list comprehensions,
    ### but it's awkward.
    def values(self):
        """
        Return a list of (bin,value) pairs, as 2-tuples.

        From this tuple list, lists of values and bins can be obtained
        using list comprehensions, as in:
        
          vals = [value for bin,value in dist1.values()]
          bins = [bin   for bin,value in dist1.values()]

        Various statistics can then be calculated if desired:
        
          sum(vals)  (total of all values)
          max(vals)  (highest value in any bin)
        """
        return self._data.items()


    def counts(self):
        """
        Return a list of (bin,count) pairs, as 2-tuples.

        From this tuple list, lists of counts and bins can be obtained
        using list comprehensions, as in:
        
          cts  = [count for bin,count in dist1.counts()]
          bins = [bin   for bin,count in dist1.counts()]

        Various statistics can then be calculated if desired:
        
          sum(counts)  (total of all counts)
          max(counts)  (highest count in any bin)
        """
        return self._counts.items()


    ### JABALERT!  Is this redundant?  Seems so.
    def num_bins(self):
        """Return the number of bins."""
        return len(self._data)


    def add(self, new_data):
        """
        Add a set of new data in the form of a dictionary of (bin,
        value) pairs.  If the bin already exists, the value is added
        to the current value.  If the bin doesn't exist, one is created
        with that value.

        Bin numbers outside axis_bounds are allowed for cyclic=True,
        but otherwise a ValueError is raised.

        If keep_peak=True, the value of the bin is the maximum of the
        current value and the supplied value.  That is, the bin stores
        the peak value seen so far.  Note that each call will increase
        the total_value and total_count (and thus decrease the
        value_mag() and count_mag()) even if the value doesn't happen
        to be the maximum seen so far, since each data point still
        helps improve the sampling and thus the confidence.
        """
        for bin in new_data.keys():

            # To do: wrap cyclic bins
            if self.cyclic==False:
                if not (self.axis_bounds[0] <= bin <= self.axis_bounds[1]):
                    raise ValueError("Bin outside bounds.")
        
            if bin not in self._data:
                self._data.update({bin: 0.0})
                self._counts.update({bin: 0})

            new_value = new_data.get(bin)
            self.total_value += new_value
            self._counts[bin] += 1
            self.total_count += 1

            if self.keep_peak == True:
                if new_value > self._data[bin]: self._data[bin]=new_value
            else:
                self._data[bin] += new_value
               

    def max_value_bin(self):
        """Return the bin with the largest value."""
        return self._data.keys()[argmax(self._data.values())]


    def weighted_average(self):
        """
        """
        if self.cyclic == True:
            return self._vector_average()
        else:
            return self._weighted_average()


    def selectivity(self):
        """
        """
        if self.cyclic == True:
            return self._vector_selectivity()
        else:
            return self._relative_selectivity()


    def weighted_sum(self):
        """Return the sum of each value times its bin."""
        return innerproduct(self._data.keys(), self._data.values()) 


    def _weighted_average(self):
        """
        Return the arithmetic average of the data on the bin_axis,
        where each bin is weighted by its value.

        For a non-cyclic distribution, this quantity is a continuous,
        interpolated equivalent for the max_value_bin().
        """
        return self._safe_divide(self.weighted_sum(),sum(self._data.values())) 


    def vector_sum(self):
        """
        Return the vector sum of the data as a tuple (magnitude, avgbinnum).

        Each bin contributes a vector of length equal to its value, at
        a direction corresponding to the bin number.  Specifically,
        the total bin number range is mapped into a direction range
        [0,2pi].
        
        For a cyclic distribution, the avgbinnum will be a continuous
        measure analogous to the max_value_bin() of the distribution.
        But this quantity has more precision than max_value_bin()
        because it is computed from the entire distribution instead of
        just the peak bin.  However, it is likely to be useful only
        for uniform or very dense sampling; with sparse, non-uniform
        sampling the estimates will be biased significantly by the
        particular samples chosen.

        The avgbinnum is not meaningful when the magnitude is 0,
        because a zero-length vector has no direction.  To find out
        whether such cases occurred, you can compare the value of
        undefined_vals before and after a series of calls to this
        function.
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


    def _vector_average(self):
        """Return the vector_sum divided by the number of bins."""
        return self._safe_divide(self.vector_sum()[0], len(self._data))


    # not tested
    def _relative_selectivity(self):
        """
        Return max_value_bin()) as a proportion of the sum_value().

        This quantity is a measure of how strongly the distribution is
        biased towards the max_value_bin().  For a smooth,
        single-lobed distribution with an inclusive, non-cyclic range,
        this quantity is an analog to vector_selectivity.  To be a
        precise analog for arbitrary distributions, it would need to
        compute some measure of the selectivity that works like the
        weighted_average() instead of the max_value_bin().  The result
        is scaled such that if all bins are identical, the selectivity
        is 0.0, and if all bins but one are zero, the selectivity is
        1.0.
        """
        # A single bin is considered fully selective (but could also
        # arguably be considered fully unselective)
        if len(self._data) <= 1: 
            return 1.0

        proportion = self._safe_divide(self._data[self.max_value_bin()],
                                       sum(self._data.values()))
        offset = 1.0/len(self._data)
        scaled = (proportion-offset)/(1.0-offset)

        # JABALERT! Can we remove these comments?  I can't follow them.
        # "Since we take the peak, negative selectivities shouldn't be possible, but just in case..."
        # So make this Number(bounds=(0.0, 1.0)) and use set_in_bounds() or something?
        return scaled 


    # not tested
    def _vector_selectivity(self):
        """
        Return the vector_mag() divided by the sum_value().

        This quantity is a vector-based measure of the peakedness of
        the distribution.  If only a single bin has a non-zero value(),
        the selectivity will be 1.0, and if all bins have the same
        value() then the selectivity will be 0.0.  Other distributions
        will result in intermediate values.

        For a distribution with a sum_value() of zero (i.e. all bins
        empty), the selectivity is undefined.  Assuming that one will
        usually be looking for high selectivity, we return zero in such
        a case so that high selectivity will not mistakenly be claimed.
        To find out whether such cases occurred, you can compare the
        value of undefined_values() before and after a series of
        calls to this function.
        """
        return self._safe_divide(self.vector_sum()[0], sum(self._data.values()))


    def value_mag(self, bin):
        """Return the value of a single bin as a proportion of total_value."""
        return self._safe_divide(self._data.get(bin), self.total_value)


    def count_mag(self, bin):
        """Return the count of a single bin as a proportion of total_count."""
        return self._safe_divide(float(self._counts.get(bin)), float(self.total_count))
        # use of float()


    def _bins_to_radians(self, bin):
        """
        Convert a bin number to a direction in radians.

        Works for Numeric arrays of bin numbers, returning
        an array of directions.
        """
        return (2*pi)*bin/self.axis_range 


    def _radians_to_bins(self, direction):
        """
        Convert a direction in radians into a bin number.

        Works for Numeric arrays of direction, returning
        an array of bin numbers.
        """
        return direction*self.axis_range/(2*pi)
        
        
    def _safe_divide(self,numerator,denominator):
        """
        Division routine that avoids division-by-zero errors
        (returning zero in such cases) but keeps track of them
        for undefined_values().
        """
        if denominator==0:
            self.undefined_vals += 1
            return 0
        else:
            return numerator/denominator


##    # not tested - will it be needed?
##    def relative_value(self, bin):
##        """
##        Return the value of the given bin as a proportion of the
##        sum_value().
##
##        This quantity is on a scale from 0.0 (the
##        specified bin is zero and others are nonzero) to 1.0 (the
##        specified bin is the only nonzero bin).  If the distribution is
##        empty the result is undefined; in such a case zero is returned
##        and the value returned by undefined_values() is incremented.
##        """
##        return self._safe_divide(self._data.get(bin), sum(self.values()))





        



    
