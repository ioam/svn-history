import param
import os, json, glob, fnmatch, copy
import numpy as np


# itertools.tee(iterator)  - works but lose useful pprinting/methods
# itertools.chain() for concat?
# "groupby() assumes that the underlying iterable’s contents will already be sorted based on the key.
#  Note that the returned iterators also use the underlying iterable, so you have to consume the results of iterator-1 before requesting iterator-2 and its corresponding key."


from dispatch import StaticSpecs

# Latex long table and poster packages
# precedence+blacklist for Latex
# root_directory now attribute


#http://www.mail-archive.com/pytables-users@lists.sourceforge.net/msg01233.html 
# """Getting a numpy.recarray from a tables.Table"""
# import numpy, tables
# f = tables.openFile("test.h5", "w")
# description = {'label': tables.StringCol(16), 
#     'x':tables.Float64Col(), 'y':tables.Float64Col()}
# t = f.createTable(f.root, "test", description)
# r = t.row
# for i in range(3): # add some data
#     r["label"] = chr(i + ord("a")) # "a", "b", ...
#     r["x"] = i * 2.5
#     r["y"] = i
#     r.append()
# t.flush()
# rec = t[:].view(numpy.recarray)

#################

import numpy as np
from itertools import groupby
tuples = [('1a','1b','1c','1d'), ('1a','1b','1c','2d'),  ('1a','1b', '1c', '3d'), ('1a','1b','2c','1d'), ('1a','1b','2c','2d'),  ('1a','2b','1c','1d'), ('1a','2b','2c','1d'), ('1a','2b','2c','5d'),   ('2a','1b','1c','1d'),('2a','1b','1c','2d'),  ('2a','1b', '1c', '3d'), ('2a','1b','2c','1d'), ('2a','1b','2c','2d'),  ('2a','2b','1c','1d'), ('2a','2b','2c','1d'), ('2a','2b','2c','5d')]

dtype=[('fst','|S2'),('snd','|S2'),('thrd','|S2'),('fth', '|S2')]
tarray = np.array(tuples, dtype=dtype)[np.random.permutation(len(tuples)) ]

ref = list( tarray[np.lexsort([tarray['snd'], tarray['fst']])]) # [fast to slow]->[left to right]



def directional_lexsort():
   pass

# - The first lexsort disambiguates ordering on one axis, leaving ambiguity of ordering along second.
# - Groupby is used to group the ambiguous records together
# - The full set of values to be laid out on second axis are found and appropriately lexsorted giving c_labels.
# - Lexsort is applied to each ambiguous group and the records are inserted into the grid in the appropriate column.


ordmapping = np.unique(tarray['snd']).tolist(); sgn=-1   # N.B: Unique also sorts..
c_lexsort =  tarray[np.lexsort([ map(lambda x: sgn*ordmapping.index(x), tarray['snd']), tarray['fst']])] # Verified int negative trick works...
r_groups = list(np.array(list(g), dtype) for (k,g) in groupby(c_lexsort, key=lambda x: x['snd']))

c_labelset = np.unique(c_lexsort[['thrd', 'fth']])
c_labels = c_labelset[np.lexsort([c_labelset['fth'], c_labelset['thrd']])].tolist()

grid = np.zeros((len(r_groups),len(c_labels)), dtype=object)

r_labels = []
for (r, r_group) in enumerate(r_groups):
   r_labels.append(r_group[['fst','snd']][0])
   r_lexsort = np.lexsort([r_group['fth'], r_group['thrd']])
   sorted_row = r_group[r_lexsort]
   c_indices = [c_labels.index(tuple(el)) for el in sorted_row[['fth','thrd']]]
   grid[r,c_indices] = sorted_row

print grid

##############

# Reportlab seems the standard (pythonic) way of generating pdfs.
# Latex with longtable.
# Or pylab.
##############

def parse_log(log_path):
    " Parses a launcher log into a spec dictionary"
    with open(log_path,'r') as log:
       splits = (line.split() for line in log)
        zipped = [(int(split[0]), json.loads(" ".join(split[1:]))) for split in splits]
    tids, specs = zip(*zipped)
    return list(tids), list(specs)


logpath="/exports/work/inf_ndtc/s0787336/topographica/dispatch/examples/Demo_Output/2012-05-02_1734-topo_local/topo_local-0.log"

tids, specs = parse_log(logpath)

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
        self.raw_array = np.array(all_values, dtype=dtypes) # Object dtype allows arbitrary length strings.
        
        # raw_array should be made available...

    def __getattr__(self, name):  
        view = self.raw_array.view(np.recarray)
        return getattr(view, name)

    def __len__(self): return len(self._raw_specs)

    def __str__(self):
        info = (len(self._raw_specs), self.spec_keys, self.kwarg_keys)
        return "Table of %d records. Spec keys: %s with data keys: %s" % info

    def selection_to_specifier(self, selection):
        assert selection.dtype == np.dtype('bool'), "Selection must by a 1D array of booleans."
        # Selection is list of bools
        fields = self.raw_array.dtype.names
        specs = [dict(zip(fields,record)) for (keep,record) in zip(selection,self.raw_array) if keep]
        return StaticSpecs(specs)

    def table_selection(self, selection):
        # Returns new Table restricted to selection.
         return Table(self.selection_to_specifier(selection))
        
    def __getitem__(self, key):
        view = self.raw_array.view(np.recarray)
        return view[key]
        #return self.recarray[key]

    def pprint(self, fields):
        # Pretty print only the selected fields
        pass

s = Table(StaticSpecs(specs), tid=tids)
print s
print s[(s.cortex_density == '1.0000') & (s.retina_density == '2.0000')].times


# SNIPPETS!
# s.recarray[np.argsort(s.cortex_density)]




class LatexGrid(param.Parameterized):

    whitelist_exts = param.List(default=['.png', '.jpeg']) # Whitelist
    
    def __init__(self, root_directory, log_name): # CUT root_directory TO GET BATCH NAME. ONLY ONE LOG NAME NOW!

        self.root_directory = root_directory

        root_path = param.normalize_path(root_directory)
        log_path = os.path.join(root_path, log_name)
        assert os.path.exists(log_path), "Log file %s does not exist! Is path prefix set?" % log_path
        tids, specs = parse_log(log_path)
        
        self.image_sets = [];  self.image_grid = None

        self.original_specs = copy.copy(specs); annotated_specs = []
        filtered = []; tids = []
        tid_directory_glob = '*_t{tid}_*'
        for (tid,spec) in enumerate(specs):
            match = glob.glob(os.path.join(root_path, tid_directory_glob.format(tid=tid)))
            assert len(match)==1, "No match or too many matches!" 
            file_paths = [os.path.join(path, fn) for (path, _, fns) in  os.walk(match[0]) for fn in fns]
            # Filter by file extensions
            filtered_files = [fp for fp in file_paths if os.path.splitext(fp)[1] in self.whitelist_exts]
            annotated_specs.append(spec)
            tids.append(tid); filtered.append(filtered_files)

        self._latex_table = Table(StaticSpecs(annotated_specs), _tid=tids, _filtered_files=filtered)
     

    def table(self): return Table(StaticSpecs(self.original_specs))

    def image_grid(self, grid2D):
        " None for empty placeholder"
        grid = np.array(grid2D)
        assert len(grid.shape) == 2, "Please supply a 2D array of image names"
        grid_names = [el for el in grid.flatten() if (el is not None)]
        assert set(grid_names).issubset(set(self.image_sets)), "Image grid must use defined image sets only!"
        self.image_grid = grid

        
    def partition_files(self, key, values, partition_fn):

        recarray = self._latex_table.raw_array
        fields = [ name for (name,_) in recarray.dtype.descr]
        assert key not in fields, "Overlapping key!"

        partitioned_specs = []; all_file_matches=[]; all_new_values = []
        for val in values:
            for (i,tid) in enumerate(recarray['_tid']):
                record = recarray[i]
                filtered_fnames = [os.path.basename(file_path) for file_path in record['_filtered_files']] 
                file_matches =  [fname for fname in filtered_fnames if partition_fn(fname,val)]
                all_new_values.append(val); all_file_matches.append(file_matches)
                partitioned_specs.append(dict(zip(fields, record)))

        kwargs = {key:all_new_values, ('_%s_partitioned_files' % key):all_file_matches}
        self._latex_table = Table(StaticSpecs(partitioned_specs), **kwargs)
        simple_specs = [ dict([(k,v) for (k,v) in  spec.items() if k[0]!='_']) for spec in partitioned_specs]
        return Table(StaticSpecs(simple_specs), **{key:all_new_values})

    def add_image_set(self, name, pattern):
        # Ensure one or zero per record.
        # name:<pattern>
        self.image_sets.append(name) # If successful.

    def keys_left_to_right(self, varying_key, decreasing_keys=False, value_orders=None):
        """ Across document """
        # if top_to_bottom defined, ensure is remaining keys
        # if top_to_bottom NOT defined, set it to remaining keys
        pass

    def keys_top_to_bottom(self, varying_key, decreasing_keys=False, value_orders=None):
        """ Across document """
        # if left_to_right defined, ensure *IS* remaining keys
        # if left_to_right NOT defined, set it to remaining keys
        pass

        # The key that varies left to right, increasing or decreasing
        # with override for order if desired.

        # varying_keys is a LIST of keys. ORDER from fastest varying to slowest varying.
        # decreasing_leys is a LIST of the keys that are decreasing.

        # Just zip three lists.
        # if decreasing_keys = False; decreasing_keys=[False]*len(keys)
        # if set_orderings is None; set_orderings=[None]*len(keys)
        # zipped = zip(keys, decreasing_keys, set_orderings)
        # assert len(zipped) == len(keys), " Length of decreasing_keys or set_orderings not length of keys!"

    def generate(self):

        # if neither top_to_bottom nor 
        # Int split varying keys in half
        
        if self.image_grid:
            # Use the grid
            pass
        else:
            # For each image file found, set the image grid to be a (1,1) and generate
            pass

param.normalize_path.prefix = os.path.join(os.getcwd(), 'examples', 'Demo_Output')
latex = LatexGrid('2012-05-02_1734-topo_local', 'topo_local-0.log') # Cut at fixed length (16) - rest is batchname



partition_fn = lambda s, v: fnmatch.fnmatch(s, '*__%s.00_*' % str(v).zfill(6))
a = latex.partition_files('time', [1,5,10], partition_fn)

#latex = LatexGrid('2012-05-02_1734-topo_local') # Cut at fixed length (16) - rest is batchname



# np.lexsort(( -np.argsort(darray['snd']), [-float(i) for i in darray['fst']], [ thrd_dict[k] for k in darray['thrd'] ] ))


#############################################################################################
       
        # As static spec, have varying keys nicely ordered - use for default behaviour!
        # Even nicer, turn selection back to spec and have NEW *CONSTRAINED* set!


    # NOTE: FILENAMES SHOULD *NOT* BE MADE PART OF TABLE:
    # THE FILES MAY HAVE SAME NAMES FROM PARAM SET TO PARAM SET 
    # *BUT* WE WANT TO CONSIDER THIS SET TO BE VARYING!

    # NOTE: Think of as treee - leaves MUST be files!


    # DEFAULT BEHAVIOUR:

    # LATEX so must be image files - already automatically extracted

    # IF *single* (or no) image each time:

    # Uses varying keys, fastest to slowest
    # left_to_right, topo_to_bottom, <rest>
    # All with defaults (ie, ascending)

    # IF *multiple* images (likely):

    # TRY fitting all images in row
    # ELSE try fitting on page
    # ELSE try fitting on multiple pages


    # SORT APPROACH:
    # try:    sort = sorted(float(el) for el in l)
    # except: sort = sorted(el for el in l)
            

    # TWO CASES:
    # One type of file per leaf. - Copy trees with all file types (DEFAULT)
    # DEFINE 


####################################################################################################

# NO NEED FOR LOG/INFO TO HAVE INDICES! (now toplevel is timestamped). 
# Consider an extend_launch helper. Takes rootdir, looks for log and extends from last tid in log



# latex.select_images(OR_pref_t1='<pattern>') # Allow specifying subdirectories. 
                                              # Warn if missing and error if multiple matches.
                                              # Method knows which keys added (ie file keys)

#print glob.glob(os.path.join(os.getcwd(), 'examples/Demo_Output/2012-05-02_1734-topo_local/*_t[0-9]*_*'))




##############################
############################




# GENERAL TODO

# - Possible that path depends on host - be careful!
# - Unify batch_name and tag. Look at directory in your reduce example for inconsistency.


# Latex module

# - Whitelist and Blacklist [.pickle, .typ, ...] (parameters with sensible default)
# - Use glob to make file selections (with *interactive*) option.
# - Makes use of the log_file -> builds a Slice.
# - Needs regexp to find folders
# - By default make latex document of *everything*

# Latex(rows, cols, pages, block1, block2, ...)
# Latex(s.retina_density = 3, np.in1d(s.cortex_density, [1,3]),  ...)
# IE. List of bools for whole length of sliceable.


# - Timestamp at toplevel file name.
# - Make tag an EXTENSION to batch_name.
# - FIX THIS TIMESTAMP. Slowest to fastest.
# - tid in name MAYBE should be at the end.



# QUESTION: How best to test the reduce functions will work before launching?

# TODO: Need way to make it easy to fix broken reduce functions. 
#       Require a way to update reduce functions for a given map function.
#       Proposal to fix if all necessary pickles available :
#
#       analysis = TopoRunBatchAnalysis.load(batch_name)
#       analysis.fix_reduce(<mapfun_name>, <fixed_reduce_fn>)

#       analysis.reduce(  analysis.restore_logfile(<path_to_log_file>))

# TODO: Setting OpenMP.
#      Lookup python. N-1 down to 2 cores.



#####################################

import sys
import numpy as np


dic1 = {'cd':'3.5', 'rd':'42.9', 'p':'test'}
dic2 = {'cd':'3.5', 'rd':'8.9', 'p':'test'}
dic3 = {'cd':'9.5', 'rd':'42.9', 'p':'test'}
dic4 = {'cd':'9.5', 'rd':'8.9', 'p':'test'}

dic5 = {'cd':'3.5', 'rd':'42.9', 'p':'test2'}
dic6 = {'cd':'3.5', 'rd':'8.9', 'p':'test2'}
dic7 = {'cd':'9.5', 'rd':'42.9', 'p':'test2'}
dic8 = {'cd':'9.5', 'rd':'8.9', 'p':'test2'}


dicts = [dic1, dic2, dic3, dic4, dic5, dic6, dic7, dic8]
data = [tuple([v for (k,v) in sorted(d.items())]) for d in dicts]
dtype= [(k, object) for k in  sorted(dic1.keys())]

t = np.array(data, dtype)
t = t.view(np.recarray)

# With extra key 'Time' and 'Value'
print t[(t.cd=='3.5') & (t.rd=='8.9')]

# Maybe a new StaticSpec called SliceSpec??
# OR a staticmethod which returns a table of this form?


x1=np.array([1,2,3,4])
x2=np.array(['a','dd','xyz','12'])
x3=np.array([1.1,2,3,4])
r = np.core.records.fromarrays([x1,x2,x3],names='a,b,c')

r.resize(5)   
r[-1]=(5,'cc',43.0)
# http://stackoverflow.com/questions/1730080/append-rows-to-a-numpy-record-array
class autorecarray(np.recarray):

    def __init__(self, *args, **kwargs):
        self._increment = 1
        np.recarray.__init__(self,*args, **kwargs)
        
    def __getitem__(self,ind):
        try:
            return np.recarray.__getitem__(self,ind)
        except IndexError:
            self.resize((self.__len__() + self._increment,),refcheck=False)
            return self.__getitem__(ind)

    def __setitem__(self,ind,y):
        try: 
            np.recarray.__setitem__(self,ind,y)
        except IndexError:
            self.resize((self.__len__()+self._increment,),refcheck=False)
            self.__setitem__(ind,y)


# a = autorecarray((1,),formats=['i4','i4'])
# a[0] = (1,2) # len(a) will now be 2
# print a

class Dummy:    
    def __init__(self, spec):
        self._spec = spec

# WRAP internal recarray. Then simply relay useful methods.
# Relay getattr (most important)



# NOTES:

# Should be 1:1 mapping between FINAL static specs object and tid....
# ROUGH IDEA

# Slice( specs | StaticSpecs, key1=[<values1>], key2=[<values2>])
# (AssertionError if added keys already in specs)
#  Relay getattr
#  Need getitem to make selections
# np.in1d([3,5,6,3,1],[1,3])


# MAYBE the LATEX takes a Slicable

# WHY NOT MAKE STATICSPECS *NOT* ABSRACT??? IS IT FUNCTIONAL ALONE?
# If so, above problem is solved!

