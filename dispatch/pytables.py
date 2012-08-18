import json, logging, os
import tables
import numpy as np
try: from collections import namedtuple
except: namedtuple = None

class GCALTable:
    # Temporary class till new system in place

    def __init__(self, name, types, group_name=None, root_dir='.'):
        self.name = name
        self.types = types
        self.dtypes = dict([(k, np.dtype(tp)) for (k,tp) in types.items()])
        fpath = os.path.join(os.path.abspath(root_dir), name+'.h5')
        self.h5file = tables.openFile(fpath, mode="a")
        group_name = name if group_name is None else group_name
        try:    self.group = self.h5file.getNode('/%s' % group_name)
        except: self.group = self.h5file.createGroup(self.h5file.root, group_name)


    def _register_array_lists(self, array_lists):
        arrays = {}
        dtypes = dict(self.dtypes.items())
        for (name, array_list) in array_lists.items():
            first_array = array_list[0]
            dtype = np.dtype((first_array.dtype.type, first_array.shape))
            dtypes[name] = dtype
            arrays[name] = array_list[:]
        return arrays, dtypes

    def write_table(self, table_name, specs, exclude_keys = [],
                    description='', primary_key = 'id', **array_lists):

        del_keys = ['dataset', 'times', 'model'] + exclude_keys
        (arrays, dtypes) = self._register_array_lists(array_lists)
        cols = [(k,tables.Col.from_dtype(dt)) for (k,dt) in dtypes.items()
                if (k not in del_keys)]
        cols += [(primary_key, tables.Col.from_dtype(np.dtype(np.int64)))]   # Add primary key
        table = self.h5file.createTable(self.group, table_name, dict(cols), description)
        trow = table.row
        for (idx, spec) in enumerate(specs):
            converted_items =  [(k,self.types[k](v)) for (k,v) in spec.items()
                                if (k not in del_keys)]
            for (k,v) in converted_items:  trow[k] = v
            for name in arrays:
                array = arrays[name][idx][:]
                trow[name] = array
            trow.append()
        self.h5file.flush()
        primary_keys = [r.nrow for r in table.iterrows()]
        table.colinstances[primary_key][:] = primary_keys[:]
        self.h5file.flush()
        return table

    def derived_VLArray(self, array_name, description, source_table, derive_fn,
                        atom=tables.ObjectAtom(), print_progress=True, **options):
        '''
        Derives a VLArray from source_table (string name) using derive_fn which takes a
        row from the source table and returns an object of type atom (default is any
        Python object)
        '''
        vlarray = self.h5file.createVLArray(self.group, array_name,
                                            atom, description, **options)
        src = self.h5file.getNode(self.group, source_table)
        total_length = len(src)
        for num, row in enumerate(src.iterrows()):
            vlarray.append((row['id'], derive_fn(row)))
            if print_progress: print 'Progress: %d/%d' % (num, total_length)
        self.h5file.flush()
        return vlarray

    def __contains__(self, item):
        ''' Note, only seem to work for the leaves. Need _v_name for Groups '''
        return item in [t.name for t in  self.h5file.listNodes(self.group)]

    def close(self):
        self.h5file.flush()
        self.h5file.close()

    def __enter__(self): return self

    def __exit__(self, type, value, traceback): self.close()


# Original attempt at using Pytables
class PyTableUtils:

    def __init__(self, h5_file, batch_name, description='', title=''):

        self.batch_name = batch_name
        self.h5file = tables.openFile(h5_file, mode="a", title = title)

        try:    self.root = self.h5file.getNode('/%s' % batch_name)
        except: self.root = self.h5file.createGroup(self.h5file.root, batch_name, description)

    def declare_group(self, name, info):

        try:
            self.h5file.getNode('/%s/%s' % (self.batch_name, name))
            print "Node already exists"
        except: self.h5file.createGroup(self.root, name, info)

    def store_array(self, group_name, array, label, **metadata):
        try: meta = json.dumps(metadata)
        except:
            logging.info("Cannot serialise metadata to json")
            return

        group = self.h5file.getNode('/%s/%s' % (self.batch_name, group_name))
        self.h5file.createArray(group, label, array, meta)
        self.h5file.flush()

    def load_node(self, group_name, label):
        h5_path = '/%s/%s' % (self.batch_name, group_name)
        return self.h5file.getNode(h5_path, label)

    def load_array(self, group_name, label, metadata=False):
        node = self.load_node(group_name, label)
        if not metadata: return node[:]
        else:            return (node[:], json.loads(node.title))

    def store_selector(self, group_name, selector, label, **metadata):
        assert 'dtype' not in metadata, "Field name dtype cannot be in metadata"
        sel_array = np.array(selector)
        meta = dict({'dtype':sel_array.dtype.descr}, **metadata)
        self.store_array(group_name, sel_array.tolist(), label, **meta)

    def load_selector(self, group_name, label):
        (sel_arr, meta) = self.load_array(group_name, label, metadata=True)
        loaded_dtype =  np.dtype([(str(name), str(tp)) for (name,tp) in meta['dtype']])
        tuple_list = [tuple(f[0]) for f in sel_arr]
        return  Select().fromarray(np.array(tuple_list, dtype=loaded_dtype))

    def close(self):
        self.h5file.flush()
        self.h5file.close()

    def __enter__(self): return self

    def __exit__(self, type, value, traceback): self.close()


#=========================#
# Depracated (hopefully!) #
#=========================#

import numpy as np
import json, os
import tables
import pickle
from tables import *
def table_from_log(log_path ='GCAL/2012-07-13_1207-GCAL/GCAL.log',times=[i*1000 for i in range(21)]):
    types = {'scale':np.float64 , 'num_orientation':np.int64,
             'lgn_density':np.float64,'retina_density':np.float64,
             'num_phase':np.int32,
             'cortex_density': np.float64,
             'homeostasis':np.bool8, 'gain_control':np.bool8}
    h5file = tables.openFile('GCAL.h5', mode="a")
    group = h5file.createGroup(h5file.root, 'GCAL')
    dtypes = [(k, np.dtype(tp)) for (k,tp) in types.items()]
    dtypes += [('selectivity', np.dtype((np.float64, (48,48))))]
    dtypes += [('preference', np.dtype((np.float64, (48,48))))]

    dtypes += [('time', np.dtype(np.float64))]
    dtypes += [('tid', np.dtype(np.int32))]

    cols = dict([(k,Col.from_dtype(dt)) for (k,dt) in dtypes])
    table = h5file.createTable(group, 'GCAL', dict(cols), "Hacked version")
    h5file.flush()
    table_row = table.row
    with open(log_path) as f:
        for l in f:
            splits = l.split(); tid = np.int32(splits[0]); j = json.loads(' '.join(splits[1:]))
            converted = [(k, types[k](j[k])) for k in types]
            for time in times:
                for mat in ['OR_preference', 'OR_selectivity']:
                    fname =  '%s@time=%d[%d]' % (mat, time, tid)
                    fpath =  os.path.abspath('GCAL/2012-07-13_1207-GCAL/%s/%s' % (mat, fname))
                    assert os.path.exists(fpath)
                    with open(fpath, 'r') as pfile:
                        unpickled = pickle.load(pfile)
                        (t, array) = unpickled
                        assert int(t) == time
                    arr_name = 'preference' if (mat == 'OR_preference') else 'selectivity'
                    table_row[arr_name] = array
                for (key,value) in converted:
                    table_row[key] = value
                table_row['time'] = np.float64(time)
                table_row['tid'] = tid
                table_row.append()
    h5file.flush()
    h5file.close()




'''
# h5py for comparison

# - Closer to HDF5/better interoperability
# - Python 3 compatible
# - Lacking query features

import h5py
import numpy as np
f = h5py.File('./test.h5')
group = f.create_group('group_example')
f['group_example']['data'] = np.array([('aaaa', 1.0, 8.0, [[1, 1, 1], [1, 1, 1]]),
        ('aaaa', 2.0, 7.4000000000000004, [[2, 2, 2], [2, 2, 2]]),
        ('bbbb', 3.5, 8.5, [[3, 3, 3], [3, 3, 3]]),
        ('aaaa', 6.4000000000000004, 4.0, [[4, 4, 4], [4, 4, 4]]),
        ('aaaa', 8.8000000000000007, 4.0999999999999996, [[5, 5, 5],
[5, 5, 5]]),
        ('bbbb', 5.5, 9.0999999999999996, [[6, 6, 6], [6, 6, 6]]),
        ('bbbb', 7.7000000000000002, 8.5, [[7, 7, 7], [7, 7, 7]])],
       dtype=[('name', '|S4'), ('x', 'f8'), ('y', 'f8'), ('block',
'i8', (2, 3))])

# NOTE: Instantiates whole recarray
# Can slice block: f['group_example']['data'][3:4]
[el['block'].shape for el in f['group_example']['data'][:]]

# Access from dataset
f['group_example']['data']['block']
f['group_example']['data'].attrs['some_metadata'] = 'This is METADATA'

# Supports numpy mask array indexing

# Specify the array data in constructor of create_dataset

# Use list() to see contents of files/groups
f.flush()
f.close()
'''


#h5f = tables.openFile('GCAL.h5', mode="a")
# ob = pickle.load(open('./GCAL/2012-07-13_1207-GCAL/OR_preference/OR_preference@time=20000[4]','r'))
# assert (ob[1] == [x['preference'] for x in h5f.root.GCAL.GCAL.iterrows() if ((x['scale'] == 0.35) and (x['time'] == 20000))][0])

# FROM VIDEO TUT
# For changing data -> call update() and then flush()
# stringCol has an itemsize argument
# For single attributes use table.column[:] (ie. slice)
