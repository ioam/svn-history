"""
Classes support robotics using Topographica.

This module contains several classes for constructing robotics
interfaces to Topographica simulations.  It includes modules that read
input from or send output to robot devices, and a (quasi) real-time
simulation object that attempts to maintain a correspondence between
simulation time and real time.

This module requires the PlayerStage robot interface system, and the
playerrobot module for high-level communications with Player robots.

$Id$
"""

__version__ = $Revision$

from topo.base.simulation import Simulation,EventProcessor
from topo.base.parameterclasses import Integer,Number,ClassSelectorParameter
from topo.patterns.image import GenericImage

from playerrobot import CameraDevice,PTZDevice

import Image,ImageOps
from math import pi,cos,sin
import time

class CameraImage(GenericImage):
    """
    An image pattern generator that gets its image from a Player
    camera device.
    """
    
    camera = ClassSelectorParameter(CameraDevice,default=None,doc="""
       An instance of playerrobot.CameraDevice to be used
       to generate images.""")

    def _get_image(self,params):
        
        fmt,w,h,bpp,fdiv,data = self.camera.image
        if fmt==1:
            self._image = Image.new('L',(w,h))
            self._image.fromstring(data,'raw')
        else:
            # JPALERT: if not grayscale, then assume color.  This
            # should be expanded for other modes.
            rgb_im = Image.new('RGB',(w,h))
            rgb_im.fromstring(data,'raw')
            self._image = ImageOps.grayscale(rgb_im)
        return True

class PTZ(EventProcessor):
    """
    Pan/Tilt/Zoom control.

    This event processor takes input events on its 'Saccade' input
    port in the form of (amplitude,direction) saccade commands (as
    produced by the topo.sheets.saccade.SaccadeController class) and
    appropriately servoes the attached PTZ object.  There is not
    currently any dynamic zoom control, though the static zoom level
    can be set as a parameter.
    """

    ptz = ClassSelectorParameter(PTZDevice,default=None,doc="""
       An instance of playerrobot.PTZDevice to be controlled.""")
    
    zoom = Number(default=120,bounds=(0,None),doc="""
       Desired FOV width in degrees.""")

    speed = Number(default=200,bounds=(0,None),doc="""
       Desired max pan/tilt speed in deg/sec.""")

    dest_ports = ["Saccade"]
    src_ports = ['State']

    def start(self):
        pass 
    def input_event(self,conn,data):
        if conn.dest_port == 'Saccade':
            # the data should be (amplitude,direction)
            amplitude,direction = data
            self.shift(amplitude,direction)

    def shift(self,amplitude,direction):

        self.debug("Executing shift, amplitude=%.2f, direction=%.2f"%(amplitude,direction))
        pan,tilt,zoom = self.ptz.state_deg       
        if amplitude < 0:
            direction *= -1
        angle = direction * pi/180
        pan += amplitude * cos(angle)
        tilt += amplitude * sin(angle)

        self.ptz.set_ws_deg(pan,tilt,self.zoom,self.speed,self.speed)




class RealTimeSimulation(Simulation):
    """
    A (quasi) real-time simulation object.

    This subclass of Simulation attempts to maintain a correspondence
    between simulation time and real time, as defined by the timescale
    parameter.  Real time simulation instances still maintain a
    nominal, discete simulation time that determines the order of
    event delivery.

    At the beginning of each simulation time epoch, the simulation
    marks the actual wall clock time.  After event delivery for that
    epoch has ended, the simulation calculates the amount of
    computation time used for event processing, and executes a real
    sleep for the remainder of the epoch.  If the computation time for
    the epoch exceeded the real time , a warning is issued and
    processing proceeds immediately to the next simulation time epoch.
    """
    timescale = Number(default=1.0,bounds=(0,None),doc="""
       The desired real length of one simulation time unit, in milliseconds.
       """)

    def __init__(self,**params):
        super(RealTimeSimulation,self).__init__(**params)
        self._real_timestamp = 0.0
        
    def run(self,*args,**kw):
        self._real_timestamp = self.real_time()
        super(RealTimeSimulation,self).run(*args,**kw)

    def real_time(self):
        return time.time() * 1000
    
    def sleep(self,delay):
        """
        Sleep for the number of real milliseconds seconds corresponding to the
        given delay, subtracting off the amount of time elapsed since the
        last sleep.
        """
        sleep_ms = delay*self.timescale-(self.real_time()-self._real_timestamp)

        if sleep_ms < 0:
            self.warning("Realtime fault. Sleep delay of %f requires realtime sleep of %.2f ms."
                         %(delay,sleep_ms))
        else:
            self.debug("sleeping. delay =",delay,"real delay =",sleep_ms,"ms.")
            time.sleep(sleep_ms/1000.0)
        self._real_timestamp = self.real_time()
        self._time += delay
    
        
