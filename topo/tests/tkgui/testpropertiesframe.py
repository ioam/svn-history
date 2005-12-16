"""
Test cases for propertiesframe.py.

$Id$
"""
__version__='$Revision$'


# CEBHACKALERT: this does not test PropertiesFrame completely.

import unittest
from Tkinter import *
from topo.tkgui import *
from topo.tkgui.propertiesframe import *

class TestPropertiesFrame(unittest.TestCase):
    def test_PropertiesFrame(self):
        root = Tk()
        root.title('Properties Frame Test')
        pp = PropertiesFrame(root,padding=0)
        pp.pack(expand=YES,fill=X)
        
        pp.add_text_property('Name', 'Jefferson Provost')
        pp.add_text_property('Addr', '1601 Faro Dr. #1504')
    
        for i in range(5):
            pp.add_text_property('Prop'+`i`, `i`)
    
        pp.add_tagged_slider_property("Volume",value='5',
                                      string_format='%d',
                                      min_value="0",max_value="11")
    
        # CEBHACKALERT: "I fix this another day"
        #pp.add_combobox_property("File",value='xxx',
        #                         scrolledlist_items=('AAA','BBB','CCC'))
        
        #target = {'Prop4': '4', 'Name': 'Jefferson Provost', 'Prop2': '2', 'Student': 1, 'Volume': '5', 'Prop0': '0', 'Prop1': '1', 'File': 'xxx', 'Prop3': '3', 'Addr': '1601 Faro Dr. #1504'}

        #values = pp.get_values()
        #if target != values:
        #    raise Exception('target != values! Failure!')
        #pp.set_values(values)
        #values = pp.get_values()
        #if target != values:
        #    raise Exception('target != pp.get_values! Failure!')


suite = unittest.TestSuite()
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPropertiesFrame))
