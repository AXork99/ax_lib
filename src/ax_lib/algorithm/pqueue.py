class pqueue:
    def __init__(self, sequence = [], key = lambda x: x, maxHeap = False):
        import heapq
        
        self.key = (lambda x: -key(x)) if maxHeap else key
        self.heap = list(map(lambda x: (self.key(x), x), sequence))
        heapq.heapify(self.heap)

    def push(self, item):
        import heapq
        heapq.heappush(self.heap, (self.key(item), item))

    def top(self):
        return self.heap[0][1]

    def pop(self):
        import heapq
        _, item = heapq.heappop(self.heap)
        return item

    def empty(self):
        return self.size() == 0
    
    def size(self):
        return len(self.heap) if self.heap else 0
    
    def merge(self, other):
        for i in other:
            self.push(i)
