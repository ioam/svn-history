"""
KeyedList sorted dictionary class.

$Id$
"""
__version__='$Revision$'

class KeyedList(list):
    """
    Extends the built-in type 'list' to support dictionary-like
    access using [].  The internal representation is as an ordinary
    list of (key,value) pairs, not a hash table like an ordinary
    dictionary, so that the elements will remain ordered.

    Note: Not all list operations will work as expected, because
    [] does not return the name tuple.

    Redefined functions:
        __getitem__ ([,])
        __setitem__ ([,])
        append  --  Now takes a tuple, (key, value) so that value
                    can be later accessed by [key].
                    
    New functions modeled from dictionaries:
        get
        set
        has_key
        keys
        items
        update
    """

    def __getitem__(self,k):
        """ The bracket [] accessor. """
        return self.get(k)

    def __setitem__(self,k,v):
        """
        The bracket [] mutator.
        Overwrite value if key already exists, otherwise append.
        """
        return self.set(k,v)

    def append(self, (key, value)):
        """
        Append a new object to the end of the existing list.

        Accepts a 2-tuple (key, value).

        Strictly speaking, this operation did not need to be redefined
        in this subclass, but by forcing the tuple in the function
        parameters, we may be able to catch an erroneous assignment.
        """
        super(KeyedList,self).append(tuple((key,value)))

    def get(self, key, default=None):
        """
        Get the value with the specified <key>.
        Returns None if no value with that key exists.
        """
        for (name,value) in self:
            if name == key:
                return value
        if isinstance(key,int):
            index = 0
            for (name,value) in self:
                if index == key:
                    return value
                else:
                    index = index + 1
            
        return default

    def set(self, key, value):
        """
        If the key already exists in the list, change the entry,
        otherwise append the new key, value to the end of the list.
        """
        for (k,v) in self:
            if k == key:
                i = self.index((k,v))
                self.pop(i)
                self.insert(i,(key, value))
                return True
        self.append((key, value))
        return True

    def has_key(self,key):
        """
        Return True iff key is found in the ordered list.
        """
        for (name,value) in self:
            if name == key:
                return True
        return False

    def items(self):
        """
        Provide function supported by dictionaries.  
        A keyed list already is stored in this format, so just returns
        the actual underlying list.
        """
        return list(self)

    def keys(self):
        """
        A copy of the list of keys.
        """
        l = [k for (k,v) in self.items()]
        return l

    def update(self,b):
        """
        updates (and overwrites) key/value pairs from b
        """
        for (k,v) in b.items():
            self.set(k,v)
