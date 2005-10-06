"""
KeyedList sorted dictionary class.

$Id$
"""

### JABHACKALERT!
###
### Need to fix the variable names and comments that are
### Topographica-specific -- nothing here should be assuming
### anything about templates or other topo-specific concepts.
class KeyedList(list):
    """
    Extends the built-in type 'list' to superficially behave like a
    dictionary with [] keyed access.  Internal representation is a
    list of (key,value) pairs.  Note: Core functionality has been
    added, but because of the way that [] does not return the name
    tuple, not all list operations may behave properly.

    Redefined functions:
        __getitem__ ([,])
        __setitem__ ([,])
        append  --  Now takes a tuple, (key, value) so that value
                    can be later accessed by [key].
    New functions modeled from dictionaries:
        get
        set
        has_key
        items
    """

    def __getitem__(self,k):
        """ The bracket [] accessor. """
        return self.get(k)

    def __setitem__(self,k,v):
        """
        The bracket [] mutator.
        Will overwrite value if key already exists, otherwise append.
        """
        return self.set(k,v)

    def append(self, (template_name, template_obj)):
        """
        Append the new PlotTemplate object to the end of the existing
        internal plot template list.

        Takes in a 2-tuple, (Name Key of new PlotTemplate, PlotTemplate Object)

        Does not have to be redefined in this subclass, but by forcing
        the tuple in the function parameters, it may catch an
        erroneous assignment.
        """
        super(KeyedList,self).append(tuple((template_name,template_obj)))

    def get(self, template_name, default=None):
        """
        Get the PlotTemplate with the key <template_name>.
        Return default (None) if it does not exist.
        """
        for (name,template_obj) in self:
            if name == template_name:
                return template_obj
        if isinstance(template_name,int):
            index = 0
            for (name,template_obj) in self:
                if index == template_name:
                    return template_obj
                else:
                    index = index + 1
            
        return default

    def set(self, template_name, template_obj):
        """
        If the template_name already exists in the list, change the
        entry, otherwise append the new template_name, template_obj to
        the end of the PlotTemplate list.
        """
        for (k,v) in self:
            if k == template_name:
                i = self.index((k,v))
                self.pop(i)
                self.insert(i,(template_name, template_obj))
                return True
        self.append((template_name, template_obj))
        return True

    def has_key(self,template_name):
        """
        Return True if template_name is a key in the ordered list.
        Return False otherwise.
        """
        for (name,template_obj) in self:
            if name == template_name:
                return True
        return False

    def items(self):
        """
        Dictionaries have this function.  A keyed list already is
        stored in this format, so just return a true list of this
        object.
        """
        return list(self)
