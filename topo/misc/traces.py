"""
Object classes for recording and plotting time-series data.

This module defines a set DataRecorder object types for recording time-series
data, a set of TraceSpecification object types for specifying ways of
generating 1D-vs-time traces from recorded data, and a TraceGroup
object that will plot a set of traces on stacked, aligned axes.


$Id$
"""
__version__ = '$Revision$'

from topo.base.simulation import EventProcessor
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number,StringParameter,DictParameter,Integer, \
     CompositeParameter,Parameter
from topo.misc.utils import Struct
from numpy import array
import bisect




class DataRecorder(EventProcessor):
    """
    Record time-series data from a simulation.

    A DataRecorder instance stores a set of named time-series
    variables, consisting of a sequence of recorded data items of any
    type, along with the times at which they were recorded.

    DataRecorder is an abstract class for which different
    implementations may exist for different means of storing recorded
    data.  For example, the subclass, InMemoryRecorder, stores all the
    data in memory.

    A DataRecorder instance can operate either as an event processor, or in a
    stand-alone mode.  Both usage modes can be used on the same
    instance in the same simulation.

    STAND-ALONE USAGE:

    A DataRecorder instance is used as follows
    
      - Method .add_variable adds a named time series variable.
      - Method .record_data records a new data item and timestamp.
      - Method .get_data gets a time-delimited sequence of data from a variable
    
    EVENTPROCESSOR USAGE:

    A DataRecorder can also be connected to a simulation as an event
    processor, forming a kind of virtual recording equipment.  An
    output port from any event processor in a simulation can be
    connected to a DataRecorder; the recorder will automaticall create
    a variable with the same name as the connection, and record any
    incoming data on that variable with the time it was received.  For
    example:

    topo.sim['Recorder'] =  InMemoryRecorder()
    topo.sim.connect('V1','Recorder',name='V1 Activity')

    This script snippet will create a new DataRecorder and
    automatically record all activity sent from the sheet 'V1'.

    """


    _abstract_class_name = "DataRecorder"

    def __init__(self,**params):
        super(DataRecorder,self).__init__(**params)
        self._trace_groups = {}


    def _src_connect(self,conn):
        raise NotImplementedError
    
    def _dest_connect(self,conn):
        super(DataRecorder,self)._dest_connect(conn)
        self.add_variable(conn.name)

    def input_event(self,conn,data):
        self.record_data(conn.name,self.simulation.time(),data)

    def add_variable(self,name):
        """
        Create a new time-series variable with the given name.
        """
        raise NotImplementedError

    def record_data(self,varname,time,data):
        """
        Record the given data item with the given timestamp in the
        named timeseries.
        """
        raise NotImplementedError

    def get_data(self,varname,times=(None,None),fill_range=False):
        """
        Get the named timeseries between the given times
        (inclusive). If fill_range is true, the returned data will
        have timepoints exactly at the start and end of
        the given timerange.  The data values at these timepoints will
        be those of the next-earlier datapoint in the series.
        
        (NOTE: fill_range can fail to create a beginning timepoint if
        the start of the time range is earlier than the first recorded datapoint.]
        """
        raise NotImplementedError

    def get_times(self,var):
        """
        Get all the timestamps for a given variable.
        """
        raise NotImplementedError

    def get_time_indices(self,varname,start_time,end_time):
        """
        For the named variable, get the start and end indices suitable
        for slicing the data to include all times t:
          start_time <= t <= end_time.

        A start_ or end_time of None is interpreted to mean the
        earliest or latest available time, respectively.
        """

        times = self.get_times(varname)
        if start_time is None:
            start = 0
        else:
            start = bisect.bisect_left(times,start_time)

        if end_time is None:
            end = None
        else:
            end = bisect.bisect_right(times,end_time)

        return start,end




                    

class InMemoryRecorder(DataRecorder):
    """
    A data recorder than stores all recorded data in memory.
    """

    def __init__(self,**params):
        super(InMemoryRecorder,self).__init__(**params)
        self._vars = {}

    def add_variable(self,name):
        self._vars[name] = Struct(time=[],data=[])

    def record_data(self,varname,time,data):
        var = self._vars[varname]

        # add the data, maintaining it sorted by time
        if not var.time or var.time[-1] <= time:
            var.time.append(time)
            var.data.append(data)
        elif time < var.time[0]:
            var.time.insert(0,time)
            var.data.insert(0,data)
        else:
            idx = bisect.bisect_right(var.time,time)
            var.time.insert(idx,time)
            var.data.insert(idx,data)

    def get_data(self,name,times=(None,None),fill_range=False):
        tstart,tend = times
        start,end = self.get_time_indices(name,tstart,tend)
        var = self._vars[name]
        time,data = var.time[start:end],var.data[start:end]
        if fill_range:
            if time[0] > tstart and start > 0:
                time.insert(0,tstart)
                data.insert(0,var.data[start-1])
            if time[-1] < tend:
                time.append(tend)
                data.append(data[-1])
        
        return time,data

    def get_times(self,varname):
        return self._vars[varname].time




class TraceSpecification(ParameterizedObject):
    """
    A specification for generating 1D traces of data from recorded
    timeseries.

    A TraceSpecification object is a callable object that encapsulates
    a method for generating a 1-dimensional trace from possibly
    multidimensional timeseries data, along with a specification for
    how to plot that data, including Y-axis boundaries and plotting arguments.
    
    TracesSpecification is an abstract class.  Subclasses implement
    the __call__ method to define how to extract a 1D trace from a
    sequence of data.
    """
    
    _abstract_class_name = "TraceSpecification"

    data_name = StringParameter(default=None,doc="""
       Name of the timeseries from which the trace is generated.
       E.g. the connection name into a DataRecorder object.
       """)

    # JPALERT: This should really be something like a NumericTuple,
    # except that NumericTuple won't allow the use of None to indicate
    # 'no default'.  (Nor will Number.)
    ybounds = Parameter(default=(None,None),doc="""
       The (min,max) boundaries for y axis.  If either is None, then
       the bound min or max of the data given, respectively.""")

    ymargin = Number(default=0.1,doc="""
       The fraction of the difference ymax-ymin to add to the
       top of the plot as padding.""")
    plotkw = DictParameter(default=dict(linestyle='steps'),doc="""
       Contains the keyword arguments to pass to the plot command
       when plotting the trace.""")
       
    def __call__(self,data):
        raise NotImplementedError

    def get_ybounds(self,ydata):
        ymin,ymax = self.ybounds
        if ymax is None:
            ymax = max(ydata)

        if ymin is None:
            ymin = min(ydata)

        ymax += (ymax-ymin)*self.ymargin

        return ymin,ymax


class IdentityTrace(TraceSpecification):
    """
    A Trace that returns the data, unmodified.
    """
    def __call__(self,data):
        return data

class IndexTrace(TraceSpecification):
    """
    A Trace that assumes that each data item is a sequence that can be
    indexed with a single integer, and traces the value of one indexed element.
    """
    index = Integer(default=0,doc="""
       The index into the data to be traced.
       """)
    
    def __call__(self,data):
        return [x[self.index] for x in data]

class SheetPositionTrace(TraceSpecification):
    """
    A trace that assumes that the data are sheet activity matrices,
    and traces the value of a given (x,y) position on the sheet.
    """
    x = Number(default=0.0,doc="""
       The x sheet-coordinate of the position to be traced.
       """)
    y = Number(default=0.0,doc="""
       The y sheet-coordinate of the position to be traced.
       """)

    position = CompositeParameter(attribs=['x','y'],doc="""
       The sheet coordinates of the position to be traced.
       """)

    # JPALERT:  Would be nice to some way to set up the coordinate frame
    # automatically.  The DataRecorder object alread knows what sheet
    # the data came from.
    coordframe = Parameter(default=None,doc="""
       The SheetCoordinateFrame to use to convert the position
       into matrix coordinates.""")

    def __call__(self,data):
        r,c = self.coordframe.sheet2matrixidx(self.x,self.y)
        return [d[r,c] for d in data]



class TraceGroup(ParameterizedObject):
    """
    A group of data traces to be plotted together.

    A TraceGroup defines a set of associated data traces and allows
    them to be plotted on stacked, aligned axes.  The constructor
    takes a DataRecorder object as a data source, and a list of
    TraceSpecification objects that indicate the traces to plot.  The
    trace specifications are stored in the attribute .traces, which
    can be modified at any time.
    """
    def __init__(self,recorder,traces=[],**params):
        super(TraceGroup,self).__init__(**params)
        self.traces = traces
        self.recorder = recorder

    def plot(self,times=(None,None)):
        """
        Plot the traces.

        Plots the traces specified in self.traces, over the timespan
        specified by times.  times = (start_time,end_time); if either
        start_time or end_time is None, it is assumed to extend to the
        beginning or end of the timeseries, respectively.
        """

        
        import pylab
        rows = len(self.traces)
        tstart,tend = times
        if tstart is None:
            tstart = 0
        if tend is None:
            # JPALERT: This should be coded more generally,
            # but this is the basic behavior we want, I think.
            tend = self.recorder.simulation.time()
        pylab.subplots_adjust(hspace=0.6)
        for i,trace in enumerate(self.traces):
            # JPALERT: The TraceGroup object should really create its
            # own matplotlib.Figure object and always plot there
            # (instead of in the frontmost plot), but I haven't
            # figured out how to do that yet.
            pylab.subplot(rows,1,i+1)
            pylab.title(trace.name)
            time,data = self.recorder.get_data(trace.data_name,times=times,fill_range=True)
            y = trace(data)
            pylab.plot(time,y,**trace.plotkw)
            ymin,ymax = trace.get_ybounds(y)
            pylab.axis(xmin=tstart,xmax=tend,ymin=ymin,ymax=ymax)        

    
