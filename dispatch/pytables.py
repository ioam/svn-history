import json, logging
import tables
import numpy as np
from dispatch.utils import Select

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
