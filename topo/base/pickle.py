"""
Temporary implementation to bypass lambda functions in disparity scripts
"""


from parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number

class PickleDisparity1(ParameterizedObject):
    
    input_param = Number(
        default=0,bounds=(-1.0,1.0),hidden=True)

    disp = Number(
        default=0,bounds=(-1.0,1.0),hidden=True)

       

    def __call__(self,**params):


        input_param=params.get('input_param',self.input_param)
        disparity=params.get('disp',self.disp)

        #print "left_eye", '--', input_param, '--' , disparity

        return input_param - disparity

class PickleDisparity2(ParameterizedObject):
    
    input_param = Number(
        default=0,bounds=(-1.0,1.0),hidden=True)

    disp = Number(
        default=0,bounds=(-1.0,1.0),hidden=True)

       

    def __call__(self,**params):


        input_param=params.get('input_param',self.input_param)
        disparity=params.get('disp',self.disp)

        #print "right_eye", '--',input_param, '--' , disparity

        return input_param + disparity
