"""
A simple priority queue with O(log n) insertionand deletion.

$Id$
"""

class Heap:
    """
    The heap class.  This class implements a priority queue on any
    objects which are comparable with <.  Lesser values get higher priority.
    """
    
    def __init__(self):
        self.__store = []

    def top(self):
        """
        Return the top (highest priority) item, but don't remove it from the
        queue.
        """
        return self.__store[0]

    def pop(self):
        """
        Remove the top item and return it. 
        """
        result = self.top()
        self.__store[0] = self.__store[-1]
        del(self.__store[-1])
        reheap_down(self.__store,0)
        return result

    def push(self,item):
        """
        Add an item to the queue.
        """
        self.__store.append(item)
        reheap_up(self.__store,len(self)-1)

    def __len__(self):
        return len(self.__store)

    def empty(self):
        return len(self) == 0




#
# Support functions
#


def reheap_down(store,pos):
    """
    Move the object at pos into place by repeatedly swapping
    it with the lesser of its children.
    """

    min_child = min_child_index(store,pos)
    
    if min_child != None and store[pos] > store[min_child]:
        temp = store[min_child]
        store[min_child] = store[pos]
        store[pos] = temp
        reheap_down(store,min_child)

def reheap_up(store,pos):
    """
    Move the object at pos into place by swapping it with its parent
    if the parent is greater.
    """

    parent_pos = parent(pos)
    
    if pos > 0 and store[parent_pos] > store[pos]:
        temp = store[parent_pos]
        store[parent_pos] = store[pos]
        store[pos] = temp
        reheap_up(store,parent_pos)

def min_child_index(store,pos):
    """
    Find the index of the child of pos with min value.  If pos is a leaf,
    return None.
    """    
    left_pos = left(pos)
    if left_pos >= len(store):
        return None
    
    right_pos = right(pos)
    if right_pos >= len(store):
        return left_pos
    
    if store[right_pos] < store[left_pos]:
        return right_pos

    return left_pos

def left(pos):
    """
    Return the index of the left child of pos in a full binary tree.
    """
    return 2*(pos+1)-1

def right(pos):
    """Return the index of the right child of pos in a full binary tree"""
    return 2*(pos+1)

def parent(pos):
    """Return the parent of pos in a full binary tree"""
    return (pos-1)/2
 
    

if __name__ == '__main__':

    from random import *
    from math import *
    print "Testing on integers: "

    h = Heap()
    for i in [floor(random()*100) for x in range(10)]:
        print "Inserting %d" % i
        h.push(i)
    for i in range(3):
        print 'Extracting %d' % h.pop()
    for i in [-1, 50, 200]:
        print 'Inserting %d' % i
        h.push(i)

    while not h.empty():
        print 'Extracting %d' % h.pop()

    print 'Empty.'

    
