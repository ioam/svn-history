import os, fnmatch
import numpy as np

from PIL import Image
import param
from dispatch.utils import Select, Collate, PILImageLoader
from dispatch.pytables import PyTableUtils


path=os.path.abspath('../topographica/Demo_Output/2012-06-01_1556-topo_analysis_local/topo_analysis_local.log')

def select():

    spec = Collate(*Collate.from_log(path))

    sel = Select(spec, float_keys=['cortex_density', 'retina_density'])

    data = np.random.rand(9)
    selection = (sel.retina_density > 3.0) & (sel.cortex_density > 5)

    assert set(sel[selection].tid) == set([5, 8])
    assert repr(sel.select(selection, data)) == repr(data[selection])

    list_data = [None, 3, False, object, 3.4, '32', np.int64, unicode, lambda x: x]
    list_selection = [True, True, False, True] + [False]*5
    assert repr(sel.select(list_selection, list_data)) == repr([None, 3,object])
    new_sel = Select(sel.tolist(selection), float_keys=['cortex_density', 'retina_density'])
    return new_sel

def collate():

    collation = Collate(*Collate.from_log(path), 
                         activity=[1,2,3,4,5,6,7,8,9])

    collation.extract_filelist('AllORPrefs', ['*_t{tid}_*/*Orientation_Preference.png'])
    # Partition these files by topo.sim.time()
    collation.partition_by_filename('AllORPrefs', 'ORPrefs', '*__{time:0>9.2f}_*', time=[1.0,5.0,10.0])
      
    collation.extract_filelist('ORSel', 
                               ['*_t{tid}_*/*_{time:0>9.2f}_*Orientation_Selectivity.png'],
                               key_type={'time':float})

    collation.extract_filelist('ColKey', 
                               ['*_t{tid}_*/*_{time:0>9.2f}_*Color_Key.png'],
                               key_type={'time':float})
    collation.show()
    return collation

def pytable_save(collation):

    loader = PILImageLoader(['.png'], transform = lambda im: im.rotate(180))
    (images, metadata, imlabels) = collation.extract_files(loader, 'ColKey','ColKeyLabels')

    sel = Select(collation, 
                   float_keys=['cortex_density', 'retina_density'], 
                   int_keys=['time', 'activity'],
                   visible_keys = ['cortex_density', 'retina_density', 'activity', 'ColKeyLabels'])

    condition = (sel.retina_density > 3.0)
    image_sel, iminfo_sel, imlabel_sel =  sel.select(condition, images, metadata, imlabels)

    with PyTableUtils('utils-test.h5', 'util_test', 'Testing purposes', title='Title') as pytable:
        pytable.declare_group('images', 'Storing images')
        pytable.declare_group('selector', 'The Select object')

        for (ims, iminfos, labels) in zip(image_sel, iminfo_sel, imlabel_sel):
            for (im, label, iminfo) in zip(ims, labels, iminfos):
                pytable.store_array('images', np.array(im), label, iminfo=iminfo)
        
        pytable.store_selector('selector', sel.subselector(condition), 'subselector')

def pytable_load():

    with PyTableUtils('utils-test.h5', 'util_test', 'Testing purposes', title='Title') as pytable:

        sub_selector =  pytable.load_selector('selector', 'subselector')
        for label_str in  sub_selector.ColKeyLabels:
            for label in label_str.split():
                imarr, info = pytable.load_array('images', label, metadata=True)
                im = Image.fromarray(imarr)
                im.save('%s.png' % label)
                print info, im
        print sub_selector.retina_density

# Demonstrate conversion back to Spec object and numpy load/save
def numpy_save(collation): pass

def numpy_load(): pass


param.normalize_path.prefix = '../topographica/Demo_Output'
if __name__ == '__main__':
    new_sel = select()
    collation = collate()
    if not os.path.exists('utils-test.h5'): pytable_save(collation)
    else:                                   pytable_load()
