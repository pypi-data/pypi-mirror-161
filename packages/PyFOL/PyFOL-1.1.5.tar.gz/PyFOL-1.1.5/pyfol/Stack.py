class Stack():
    def __init__(self):
        self.top = 0
        self.stacklst = []
        
    def isempty(self):
        return self.top==0
    
    def height(self):
        return self.top
    
    def push(self,value):
        self.stacklst.append(value)
        self.top += 1
        
    def pop(self):
        self.stacklst.pop()
        
# stack = Stack()
# print(stack.isempty())
# stack.push(123)
# print(stack.isempty())
# print(stack.height())
# stack.push(456)
# stack.push(789)
# stack.pop()
# print(stack.stacklst)