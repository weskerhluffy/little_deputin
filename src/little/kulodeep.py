'''
Created on 14/12/2016

@author:
'''

import logging
import sys
nivel_log = logging.ERROR
#nivel_log = logging.DEBUG
logger_cagada = None

# http://stackoverflow.com/questions/280243/python-linked-list

def _ref(obj):
    """
    weakref.ref has a bit of braindamage: you can't take a weakref to None.
    This is a major hassle and a needless limitation; work around it.
    """
    from weakref import ref
    if obj is None:
        class NullRef(object):
            def __call__(self): return None
        return NullRef()
    else:
        return ref(obj)

class _node(object):
    def __init__(self, obj):
        self.obj = obj
        self._next = None
        self._prev = _ref(None)
    def __repr__(self):
        return "node(%s)" % repr(self.obj)

    def __call__(self):
        return self.obj

    @property
    def next(self):
        return self._next

    @property
    def prev(self):
        return self._prev()

# Implementation note: all "_last" and "prev" links are weakrefs, to prevent circular references.
# This is important; if we don't do this, every list will be a big circular reference.  This would
# affect collection of the actual objects in the list, not just our node objects.
#
# This means that _node objects can't exist on their own; they must be part of a list, or nodes
# in the list will be collected.  We also have to pay attention to references when we move nodes
# from one list to another.
class llist(object):
    """
    Implements a doubly-linked list.
    """
    def __init__(self, init=None):
        self._first = None
        self._last = _ref(None)
        if init is not None:
            self.extend(init)

    def insert(self, item, node=None):
        """
        Insert item before node.  If node is None, insert at the end of the list.
        Return the node created for item.

        >>> l = llist()
        >>> a = l.insert(1)
        >>> b = l.insert(2)
        >>> d = l.insert(4)
        >>> l._check()
        [1, 2, 4]
        >>> c = l.insert(3, d)
        >>> l._check()
        [1, 2, 3, 4]
        """
        item = _node(item)

        if node is None:
            if self._last() is not None:
                self._last()._next = item
                item._prev = _ref(self._last())
            self._last = _ref(item)
            if self._first is None:
                self._first = item
        else:
            assert self._first is not None, "insertion node must be None when the list is empty"
            if node._prev() is not None:
                node._prev()._next = item
            item._prev = node._prev
            item._next = node
            node._prev = _ref(item)
            if node is self._first:
                self._first = item
        return item

    def remove(self, node):
        """
        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> d = l.append(4)
        >>> e = l.append(5)
        >>> l.remove(c) # Check removing from the middle
        3
        >>> l._check()
        [1, 2, 4, 5]
        >>> l.remove(a) # Check removing from the start
        1
        >>> l._check()
        [2, 4, 5]
        >>> l.remove(e) # Check removing from the end
        5
        >>> l._check()
        [2, 4]
        """
        if self._first is node:
            self._first = node._next
        if self._last() is node:
            self._last = node._prev
        if node._next is not None:
            node._next._prev = node._prev
        if node._prev() is not None:
            node._prev()._next = node._next
        node._next = None
        node._prev = _ref(None)
        return node.obj

    def __nonzero__(self):
        """
        A list is true if it has any elements.

        >>> l = llist()
        >>> bool(l)
        False
        >>> l = llist([1])
        >>> bool(l)
        True
        """
        return self._first is not None


    def __iter__(self):
        """
        >>> l = llist([1,2,3])
        >>> [i() for i in l]
        [1, 2, 3]
        """
        return self.getiter(self._first, self._last())

    def _check(self):
        if self._last() is None:
            assert self._last() is None
            return []
        node = self._first
        ret = []
        while node is not None:
            if node._next is None:
                assert node == self._last()
            if node._prev() is None:
                assert node == self._first
            if node._next is not None:
                assert node._next._prev() == node
            if node._prev() is not None:
                assert node._prev()._next == node
            ret.append(node.obj)
            node = node._next
        return ret

    def getiter(self, first, last):
        """
        Return an iterator over [first,last].

        >>> l = llist()
        >>> l.append(1)
        node(1)
        >>> start = l.append(2)
        >>> l.extend([3,4,5,6])
        >>> end = l.append(7)
        >>> l.extend([8,9])
        >>> [i() for i in l.getiter(start, end)]
        [2, 3, 4, 5, 6, 7]
        """
        class listiter(object):
            def __init__(self, first, last):
                self.node = first
                self.final_node = last

            def __iter__(self): return self
            def next(self):
                ret = self.node
                if ret is None:
                    raise StopIteration
                if ret is self.final_node:
                    self.node = None
                else:
                    self.node = self.node._next
                return ret
        return listiter(first, last)

    def append(self, item):
        """
        Add an item to the end of the list.

        >>> l = llist()
        >>> l.append(1)
        node(1)
        >>> l.append(2)
        node(2)
        >>> l._check()
        [1, 2]
        """
        return self.insert(item, None)

    def appendleft(self, item):
        """
        Add an item to the beginning of the list.

        >>> l = llist()
        >>> l.appendleft(1)
        node(1)
        >>> l.appendleft(2)
        node(2)
        >>> l._check()
        [2, 1]
        """
        return self.insert(item, self._first)

    def pop(self):
        """
        Remove an item from the end of the list and return it.

        >>> l = llist([1,2,3])
        >>> l.pop()
        3
        >>> l.pop()
        2
        >>> l.pop()
        1
        >>> l.pop()
        Traceback (most recent call last):
        ...
        IndexError: pop from empty llist
        """
        if self._last() is None:
            raise IndexError
        return self.remove(self._last())

    def popleft(self):
        """
        Remove an item from the beginning of the list and return it.

        >>> l = llist([1,2,3])
        >>> l.popleft()
        1
        >>> l.popleft()
        2
        >>> l.popleft()
        3
        >>> l.popleft()
        Traceback (most recent call last):
        ...
        IndexError: popleft from empty llist
        """
        if self._first is None:
            raise IndexError
        return self.remove(self._first)

    def splice(self, source, node=None):
        """
        Splice the contents of source into this list before node; if node is None, insert at
        the end.  Empty source_list.  Return the first and last nodes that were moved.

        # Test inserting at the beginning.
        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> l2 = llist([4,5,6])
        >>> l.splice(l2, a)
        (node(4), node(6))
        >>> l._check()
        [4, 5, 6, 1, 2, 3]
        >>> l2._check()
        []

        # Test inserting in the middle.
        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> l2 = llist([4,5,6])
        >>> l.splice(l2, b)
        (node(4), node(6))
        >>> l._check()
        [1, 4, 5, 6, 2, 3]
        >>> l2._check()
        []

        # Test inserting at the end.
        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> l2 = llist([4,5,6])
        >>> l.splice(l2, None)
        (node(4), node(6))
        >>> l._check()
        [1, 2, 3, 4, 5, 6]
        >>> l2._check()
        []

        # Test inserting a list with a single item.
        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> l2 = llist([4])
        >>> l.splice(l2, b)
        (node(4), node(4))
        >>> l._check()
        [1, 4, 2, 3]
        >>> l2._check()
        []
        """
        if source._first is None:
            return
        first = source._first
        last = source._last()

        if node is None:
            if self._last() is not None:
                self._last()._next = source._first
            source._first._prev = self._last
            self._last = source._last
            if self._first is None:
                self._first = source._first
        else:
            source._first._prev = node._prev
            source._last()._next = node
            if node._prev() is not None:
                node._prev()._next = source._first
            node._prev = source._last
            if node is self._first:
                self._first = source._first
        source._first = None
        source._last = _ref(None)
        return first, last

    def split(self, start, end=None):
        """
        Remove all items between [node, end] and return them in a new list.  If end is None,
        remove until the end of the list.

        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> d = l.append(4)
        >>> e = l.append(5)
        >>> l._check()
        [1, 2, 3, 4, 5]
        >>> l2 = l.split(c, e)
        >>> l._check()
        [1, 2]
        >>> l2._check()
        [3, 4, 5]

        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> d = l.append(4)
        >>> e = l.append(5)
        >>> l2 = l.split(a, c)
        >>> l._check()
        [4, 5]
        >>> l2._check()
        [1, 2, 3]

        >>> l = llist()
        >>> a = l.append(1)
        >>> b = l.append(2)
        >>> c = l.append(3)
        >>> d = l.append(4)
        >>> e = l.append(5)
        >>> l2 = l.split(b, d)
        >>> l._check()
        [1, 5]
        >>> l2._check()
        [2, 3, 4]
        """
        if end is None:
            end = self._last()

        ret = llist()

        # First, move the region into the new list.  It's important to do this first, or
        # once we remove the nodes from the old list, they'll be held only by weakrefs and
        # nodes could end up being collected before we put it into the new one.
        ret._first = start
        ret._last = _ref(end)

        # Hook our own nodes back together.
        if start is self._first:
            self._first = end._next
        if end is self._last():
            self._last = start._prev

        if start._prev() is not None:
            start._prev()._next = end._next
        if end._next is not None:
            end._next._prev = start._prev
        start._prev = _ref(None)
        end._next = None

        return ret

    def extend(self, items):
        """
        >>> l = llist()
        >>> l.extend([1,2,3,4,5])
        >>> l._check()
        [1, 2, 3, 4, 5]
        """
        for item in items:
            self.append(item)
            
    def __str__(self):
        if self._first != None:
            current = self._first
            out = 'LinkedList [' + str(current.obj) + ' '
            while current._next != None:
                current = current._next
                out += str(current.obj) + ' '
            return out + ']'
        return 'LinkedList []'


def pekeno_deputo_core(numeros):
    conta_cacas = 0
    tam_nums = len(numeros)
    numeros_ord = sorted(numeros, reverse=True)
    lista_mierda = llist(numeros_ord)
    
    logger_cagada.debug("numeros ord %s" % numeros_ord)
    
    logger_cagada.debug("la lista es %s" % lista_mierda)
    
    while(lista_mierda.__nonzero__()):
        caca_act = lista_mierda.popleft()
        logger_cagada.debug("la caca a utlizar %u" % caca_act)
        
        nodo_act = lista_mierda._first
        while(lista_mierda and nodo_act):
            sig_nodo = None
            if(caca_act > nodo_act.obj):
                caca_act = nodo_act.obj
                sig_nodo = nodo_act._next
                lista_mierda.remove(nodo_act)
            else:
                sig_nodo = nodo_act._next
            nodo_act = sig_nodo
        
        conta_cacas += 1
    
    return conta_cacas

def pekeno_deputo_main():
    
    num_casos = int(sys.stdin.readline())
    logger_cagada.debug("el num de cacasos %u" % num_casos)
    
    for _ in range(num_casos):
        numeros = []
        
        num_numeros = int(sys.stdin.readline())
        logger_cagada.debug("num de nums %u" % num_numeros)
        
        for num_num in range(num_numeros):
            num_act = int(sys.stdin.readline())
            numeros.append(num_act)
        
        logger_cagada.debug("los nums del caso actual %s" % numeros)
        
        pinche = pekeno_deputo_core(numeros)
        
        logger_cagada.debug("las cacas necesarias %u" % pinche)
        print("%u" % pinche)

if __name__ == '__main__':
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
        logging.basicConfig(level=nivel_log, format=FORMAT)
        logger_cagada = logging.getLogger("asa")
        logger_cagada.setLevel(nivel_log)   
        pekeno_deputo_main()
