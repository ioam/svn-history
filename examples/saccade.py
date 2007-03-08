"""
Sheets for simulating a moving eye.

This module provides two classes, ShiftingGeneratorSheet, and
SaccadeController, that can be used to simulate a moving eye,
controlled by topographic neural activity from structures like the
superior colliculus.

ShiftingGeneratorSheet is a subclass of GeneratorSheet that accepts a
saccade command on the 'Saccade' port in the form of a tuple:
(amplitude,direction), specified in degrees.  It shifts its sheet
bounds in response to this command, keeping the centroid of the bounds
within a prespecified boundingregion.

SaccadeController is a subclass of CFSheet that accepts CF projections
and decodes its resulting activity into a saccade command suitable for
controlling a ShiftingGeneratorSheet.


$Id$
"""
__version__ = '$Revision$'

from numpy import dot,sin,cos,pi,array

from topo.base.cf import CFSheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.parameterclasses import Number,Magnitude,Enumeration
from topo.base.boundingregion import BoundingBox,BoundingRegionParameter
from topo.misc import utils


class SaccadeController(CFSheet):
    """
    This accepts CF-projected input and computes its activity like a
    normal CFSheet, then decodes that activity into saccade amplitude
    and direction as would be specified by activity in the superior
    colliculi.  The X dimension of activity corresponds to amplitude,
    the Y dimension to direction.  The activity is decoded to a single
    (x,y) point according the the parameter decode_method.

    From this (x,y) point an (amplitude,direction) pair, specified in
    degrees, is computed using the parameters amplitude_scale and
    direction scale.  That pair is then sent out on the 'Saccade'
    output port.

    NOTE: Non-linear mappings for saccade commands, as in (Ottes, et
    al), are assumed to be provided using the x and y_mapping
    parameters of the incoming CFProjection.

    References:
    Ottes, van Gisbergen, Egglermont. 1986.  Visuomotor fields of the
    superior colliculus: a quantitative model.  Vision Research;
    26(6): 857-73.
    """

    amplitude_scale = Number(default=120,doc=
        """
        Scale factor for saccade command amplitude, expressed in
        degrees per unit of sheet.  Indicates how large a
        saccade is represented by the x-component of the command
        input.
        """)
    direction_scale = Number(default=180,doc=
        """
        Scale factor for saccade command direction, expressed in
        degrees per unit of sheet.  Indicates what direction of saccade
        is represented by the y-component of the command input.  
        """ )

    # JPALERT: For generality, decode_method should really be a
    # CallableParameter that directly specifies the fn for decoding
    # the activity into a saccade, but you can't specify a class
    # method until the class has been fully defined, so we can't
    # specify the default as SaccadeController.activity_centroid.  If
    # the decoding methods (activity_centroid, activity_sample,
    # activity_mode) are promoted to a superclass, then this parameter
    # can be changed to a CallableParameter. (with the necessary
    # internal changes in .activate()).

    decode_method = Enumeration(default='centroid',
                                available=['centroid','sample','mode'],
                                instantiate=False,
                                doc=
        """
        Selects the method for decoding activity into a saccade
        command.  Choices are:

           'centroid' -- computes the (weighted) centroid of the activity.
           'sample'   -- Treats activity as a probability distribution and
                         samples from that distribution.
           'mode'     -- Takes the mode (highest point) of the a activity.
                         If activity has multiple equal modes, will always select
                         the one with the lowest matrix coordinates.           
        """)


    src_ports = ['Activity','Saccade']

    def activate(self):
        super(SaccadeController,self).activate()

        decode_fn = getattr(self,'activity_'+self.decode_method)
            
        # get the input projection activity            
        # decode the input projection activity as a command
        xa,ya = decode_fn(self.activity)
        self.verbose("Saccade command centroid = (%.2f,%.2f)"%(xa,ya))
        
        amplitude = xa * self.amplitude_scale
        direction = ya * self.direction_scale

        self.verbose("Saccade amplitute = %.2f."%amplitude)
        self.verbose("Saccade direction = %.2f."%direction)
        
        self.send_output(src_port='Saccade',data=(amplitude,direction))



    # JPALERT: The next three methods (activity_centroid,
    # activity_sample, and activity_mode) could actually apply to any
    # Sheet.  Maybe they should be promoted?
                         
    def activity_centroid(self,activity=None):
        """
        Returns the sheet coords of the (weighted) centroid of the
        activity of the sheet, if activity argument is not None, then
        it is used instead of self.activity.
        """
        
        if activity is None:
            activity = self.activity

        ys = self.sheet_rows()
        xs = self.sheet_cols()
        
        xy = array([(x,y) for y in reversed(ys) for x in xs])
        a = activity.flat

        ## JPALERT: should optimize here to only compute centroid from
        ## active (non-zero) units.  Should be a couple lines of numpy commands.

        return utils.centroid(xy,a)
      
    def activity_sample(self,activity=None):
        """
        Samples from the sheet activity as if it were a probability
        distribution.  Returns the sheet coordinates of the sampled unit.
        If activity is not None, it is used instead of self.activity.
        """

        if activity is None:
            activity = self.activity
        idx = utils.weighted_sample_idx(activity.ravel())
        r,c = utils.idx2rowcol(idx,activity.shape)
        
        return self.matrix2sheet(r,c)

    def activity_mode(self,activity=None):
        """
        Returns the sheet coordinates of the mode (highest value) of
        the sheet activity.   
        """

        # JPHACKALERT:  The mode is computed using numpy.argmax, and
        # thus for distributions with multiple equal-valued modes, the
        # result will have a systematic bias toward higher x and lower
        # y values. (in that order).  Function may still be useful for
        # unimodal activity distributions, or sheets without limiting/squashing
        # output functions.
        
        if activity is None:
            activity = self.activity
        idx = numpy.argmax(activity.flat)
        r,c = utils.idx2rowcol(idx,activity.shape)
        return self.matrix2sheet(r,c)
      
        
class ShiftingGeneratorSheet(GeneratorSheet):
    """
    A GeneratorSheet that takes an extra  input on port 'Saccade'
    that specifies a saccade command as a tuple (amplitude,direction),
    indicating the relative size and direction of the saccade in
    degrees.  The parameter visual_angle_scale defines the
    relationship between degrees and sheet coordinates.  The parameter
    saccade bounds limits the region within which the saccades may occur.
    """

    visual_angle_scale = Number(default=90,doc=
        """
        The scale factor deterimining the visual angle subtended by this sheet, in
        degrees per unit of sheet.
        """)

    saccade_bounds = BoundingRegionParameter(default=BoundingBox(radius=1.0),doc=
        """
        The bounds for saccades.  Saccades are constrained such that the centroid of the
        sheet bounds remains within this region.
        """)

    dest_ports = ["Trigger","Saccade"]

    def input_event(self,conn,data):

        if conn.dest_port == 'Saccade':


            # JPALERT:  Right now this method assumes that we're doing
            # colliculus-style saccades. i.e. amplitude and direction
            # relative to the current position.  Technically it would
            # not be hard to also support absolute or relative x,y
            # commands, and select what style to use with either with
            # a parameter, or with a different input port (e.g. 'xy
            # relative', 'xy absolute' etc.

            # JPHACKALERT: Currently there is no support for the fact
            # that saccades actually take time, and larger amplitudes
            # take more time than small amplitudes.  No clue if we
            # should do that, or how, or what gets sent out while the
            # saccade "eye" is moving.
            
            assert not self._out_of_bounds()

            # the data should be (amplitude,direction)
            amplitude,direction = data

            # 4. convert the command to x/y translation
            radius = amplitude/self.visual_angle_scale

            # if the amplitude is negative, negate the direction (so up is still up)
            if radius < 0.0:
                direction *= -1

            self._shift(radius,direction)

            if self._out_of_bounds():
                self._find_saccade_in_bounds(radius,direction)
        else:
            super(ShiftingGeneratorSheet,self).input_event(conn,data)


    def _shift(self,radius,angle):
        angle *= pi/180
        xoff = radius * cos( angle )
        yoff = radius * sin( angle )
        # apply translation to bbox.
        self.verbose("Applying translation vector (%.2f,%.2f)"%(xoff,yoff))
        self.bounds.translate(xoff,yoff)

    def _out_of_bounds(self):
        """
        True if the centroid of the current bounds is outside the
        saccade bounds.
        """
        return not self.saccade_bounds.contains(*self.bounds.aarect().centroid())

    def _find_saccade_in_bounds(self,radius,theta):
        """
        Find a saccade in the given direction (theta) that lies within
        self.saccade_bounds.  Assumes that the given saccade was
        already performed and landed out of bounds.
        """

        # JPHACKALERT: This method iterates to search for a saccade
        # that lies in bounds along the saccade vector. We should
        # really compute this algebraically. Doing so involves computing
        # the intersection of the saccade vector with the saccade
        # bounds.  Ideally, each type of BoundingRegion would know how
        # to compute its own intersection with a given line (should be easy for
        # boxes, circles, and ellipses, at least.)


        # Assume we're starting out of bounds, so start by shifting
        # back to the original position        
        self._shift(-radius,theta)

        while not self._out_of_bounds():
            radius *= 0.5
            self._shift(radius,theta)

        radius = -radius
        while self._out_of_bounds():
            radius *= 0.5
            self._shift(radius,theta)








        
