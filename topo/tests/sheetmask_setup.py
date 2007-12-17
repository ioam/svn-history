from topo.base.projection import SheetMask,ProjectionSheet
from numpy import zeros

class LeftColMask(SheetMask):

    def reset(self):
        self._data = zeros(self.sheet.shape)
        self._data[:,0] += 1

class RightColMask(SheetMask):

    def reset(self):
        self._data = zeros(self.sheet.shape)
        self._data[:,-1] += 1

class TopRowMask(SheetMask):

    def reset(self):
        self._data = zeros(self.sheet.shape)
        self._data[0,:] += 1

class BottomRowMask(SheetMask):

    def reset(self):
        self._data = zeros(self.sheet.shape)
        self._data[-1,:] += 1
        
