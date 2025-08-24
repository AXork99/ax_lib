class Tournament:
    from ..std.utils import Identifiable
    
    class Node(Identifiable):
        def __init__(self, data = None, children = set()):
            super().__init__()
            
            self.parent : Tournament.Node = None
            self.data = data
            
            self.children : set[Tournament.Node] =  set()
            for child in children:
                self.add_child(child)
            
        def add_child(self, child : 'Tournament.Node'):
            self.children.add(child)
            child.parent = self
            
        def __repr__(self):
            return f"{self.id} : {self.data}"
            
    def __init__(self, sequence = [], key = lambda x: x, reverse = False):
        self.key = (lambda x: -key(x)) if reverse else key
        
        self.bottom : list[Tournament.Node] = []
        self.top_ : Tournament.Node = None
        self.last : Tournament.Node = None
        
        self.index = {}
        self.priority = {}
        
        for s in sequence:
            self.add(s)
    
    def add(self, val):
        me = Tournament.Node(val)
        self.bottom.append(me)
        
        last = self.last
        self.last = me
        
        if len(self.bottom) == 1:
            self.top_ = me
        elif len(self.bottom) == 2:
            self.top_ = Tournament.Node(children={self.top_, me})
        else:
            other = last.parent
            while other.parent is not None and len(other.children) == 2:
                other = other.parent
                me = Tournament.Node(val, children={me})
                
            if len(other.children) == 2:
                me = Tournament.Node(val, children={me})
                other = Tournament.Node(children={other})
                self.top_ = other
            
            other.add_child(me)
        
        i = len(self.bottom) - 1
        self.index[val] = i
        self.priority[val] = self.key(val)
        
        self.update(self.last.data)
    
    def update(self, val, nval = None, norefresh = False):
        if val not in self.index:
            raise IndexError(f'Value {val} not in tournament! Values {self.index.keys()}')
        
        def f(node: Tournament.Node):
            node.data = max(map(lambda x: x.data, node.children), key=self.priority.get)
            if node.parent is not None:
                f(node.parent)
        
        index = self.index[val]
        try:
            node : Tournament.Node = self.bottom[index]
        except IndexError as e:
            e.add_note(f"Value: {val} with index {index} not in tournament {self.bottom}")
            raise e
        
        if nval:
            self.index.pop(val)
            val = nval
            node.data = val 
            self.index[val] = index
        
        if not norefresh:
            self.priority[val] = self.key(val)

        if node.parent:
            f(node.parent)
    
    def remove(self, val):
        if val not in self.index:
            raise IndexError(f'Value {val} not in tournament! Values {self.index.keys()}')
        
        last = self.bottom.pop()
        
        if (i := self.index[val]) < len(self.bottom):
            self.bottom[i].data = last.data
            self.index[last.data] = i
            self.update(last.data, norefresh=True)
        
        self.index.pop(val)
        self.priority.pop(val)
        
        while not last.children:
            last.parent.children.remove(last)
            last = last.parent
        
        i = len(self.bottom) - 1
        self.last = self.bottom[i]
        
        self.update(self.last.data, norefresh=True)
    
    def print(self):
        print("BOTTOM", self.bottom)
        print("INDEX", self.index)
    
    def top(self):
        return self.top_.data

if __name__ == "__main__":
    from ..std.utils import unordered
    
    t = Tournament((unordered(3, 4), unordered(1, 2), unordered(2, 2), unordered(1, 1)))
    t.print()
    t.remove(unordered(4, 3))
    t.print()
    t.update(unordered(1, 1), unordered(12, 12))
    t.print()
    t.remove(unordered(2, 2))
    t.add(unordered(23, 1))
    t.remove(unordered(2, 1))
    t.print()
    print(t.top())