class Queue():
    def __init__(self,maxlen):
        self.queuelst = []
        self.front = 0
        self.rear = -1
        self.maxlen = maxlen
        self.len = 0
        
    def isempty(self):
        return self.len == 0
    
    def isfull(self):
        return self.maxlen == self.len
    
    def length(self):
        return self.len
    
    def put(self,value):
        if self.isfull == True:
            return False
        self.queuelst.append(value)
        self.rear += 1
        self.len += 1
        
    def leave(self):
        del self.queuelst[self.front]
        self.len -= 1
        
    def show(self):
        return self.queuelst
    
# queue = Queue(4)
# print(queue.isempty())
# print(queue.maxlen,queue.len)
# print(queue.isfull())
# queue.put(1)
# queue.put(2)
# queue.put(3)
# queue.put(4)
# print(queue.isfull())
# print(queue.length())
# queue.leave()
# queue.leave()
# print(queue.queuelst)
    