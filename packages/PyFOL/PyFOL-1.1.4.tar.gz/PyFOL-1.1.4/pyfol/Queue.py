class Queue():
    def __init__(self,maxlen):
        self.queuelst = []
        self.front = 0
        self.rear = -1
        self.maxlen = maxlen
        self.len = self.rear+1 - self.front
        
    def isempty(self):
        return self.front==0 and self.rear==-1
    
    def isfull(self):
        return self.maxlen == self.len
    
    def length(self):
        return self.len
    
    def put(self,value):
        # if self.isfull:
        #     return False
        self.queuelst.append(value)
        self.rear += 1
        
    def leave(self):
        del self.queuelst[self.front]
    
# queue = Queue(4)
# queue.put(1)
# queue.put(2)
# queue.put(3)
# queue.put(4)
# queue.pop()
# queue.pop()
# print(queue.queuelst)
    