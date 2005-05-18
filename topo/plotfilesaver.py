"""
File saving routines for plots.

STATUS 6/18/05: Little more than a stub, with one class that calls a
subroutine depending on the type of plot requested.  Not yet clear if
this class should be desined with the command-line interface in mind
(IE: minimal typing, function parameters, etc.)

$Id$
"""
import topo
import topo.base
import topo.plotengine
from topo.utils import *

class PlotFileSaver(topo.base.TopoObject):
    def __init__(self,plot_type='Activation',**config):
        super(PlotFileSaver,self).__init__(**config)
        self.pe = topo.plotengine.PlotEngine(topo.simulator.active_sim())
        self.name_prefix = ''
        self.bitmaps = []

        if plot_type == 'Activation':
            self.activation_save()
        elif plot_type == 'Weights':
            self.weights_save(config['x'],config['y'],sheetname)
        elif plot_type == 'WeightsArray':
            self.weightsarray_save()
        else:
            self.warning('Unknown plot type to save.')
        self.save_to_disk()


    def save_to_disk(self):
        if self.bitmaps:
            for i in range(len(self.bitmaps)):
                self.bitmaps[i].bitmap.save(self.name_prefix + str(i)+'.jpg')
                self.message('Saving', str(i) + '.jpg')

    def activation_save(self):
        pg = self.pe.get_plot_group('Activation','ActivationPlotGroup')
        self.name_prefix = 'activation_'
        self.bitmaps = pg.load_images()

    def weights_save(self,x,y,sheetname):
        pg = self.pe.get_plot_group(('Weights',str(x),str(y)),
                                    'WeightsPlotGroup',
                                    sheetname)
        self.name_prefix = 'Weights_'
        self.bitmaps = pg.load_images()
        

    def weightsarray_save(self):
        pass
