



# arr = numpy.array([('hi','bi','lioop'),('ggg','klh','fgfgsf')]
# Can assign fields to dtype AFTER then view as recarray

# NOTE: Numpy seems to convert ints to strings (common datatype) without explicit dtype.

# h5file = tables.openFile("tutorial1.h5", mode = "w", title = "Test file")
# group = h5file.createGroup("/", 'batch_name', 'Batch description')

# Does not work with object dtype...
# table = h5file.createTable(group, 'readout', arr, "The table")
# table.flush()
# trec = table[:].view(numpy.recarray)


# NOTE that both pyTables and numpy.arrays can be viewed as recarrays!


import param


class Table(param.Parameterized):
    " Missing value is None (keys and value always strings so this is unambiguous) "

    print_keys = param.List(default=None, allow_None)

    def __init__(self, static_spec, **kwargs):

        self._raw_specs = static_spec.next()
        self.spec_keys = sorted(set([ str(k) for spec in self._raw_specs for k in spec.keys()]))
        self.kwarg_keys = sorted(str(k) for k in kwargs.keys())

        overlapping_keys = set(self.spec_keys) & set(self.kwarg_keys)
        assert overlapping_keys == set(), "Overlapping keys: %s" % list(overlapping_keys)
        assert all([len(l)==len(self._raw_specs) for l in kwargs.values()]), " Value lists must match length of spec!"

        spec_values = [tuple([str(spec.get(k)) for k in self.spec_keys]) for spec in self._raw_specs]
        all_values = [v + tuple([kwargs[k][i] for k in self.kwarg_keys]) 
                      for (i,v) in enumerate(spec_values)]    
        dtypes= [(str(k), object) for k in  self.spec_keys + self.kwarg_keys] 
        self.source = np.array(all_values, dtype=dtypes) # Object dtype allows arbitrary length strings.
        
        # source should be made available...


    def save_h5(self, filename, description):
        try: import tables 
        except: "Cannot import pyTables"; return

    def load_h5(self, filename):
        try: import tables 
        except: "Cannot import pyTables"; return
        

    def __getattr__(self, name):  
        view = self.source.view(np.recarray)
        return getattr(view, name)

    def __len__(self): return len(self._raw_specs)

    def __str__(self):
        info = (len(self._raw_specs), self.spec_keys, self.kwarg_keys)
        return "Table of %d records. Spec keys: %s with data keys: %s" % info

    def to_staticspecs(self, selection):
        assert selection.dtype == np.dtype('bool'), "Selection must by a 1D array of booleans."
        # Selection is list of bools
        fields = self.source.dtype.names
        specs = [dict(zip(fields,record)) for (keep,record) in zip(selection,self.source) if keep]
        return StaticSpecs(specs)

    def table_selection(self, selection):
        # Returns new Table restricted to selection.
         return Table(self.selection_to_specifier(selection))
        
    def __getitem__(self, key):
        view = self.source.view(np.recarray)
        return view[key]
        #return self.recarray[key]

    def pprint(self, fields):
        # Pretty print only the selected fields
        pass

