class Node():
    def __init__(self,value=None,next=None):
        self.value = value
        self.next = next
            
class UnidirectionalLinkedList():
    def __init__(self):
        self.head = None
        self.tail = None
        self.len = 0
    
    def isempty(self):
        return self.head == None
    
    def length(self):
        return self.len
    
    def append(self,value):
        if self.head == None:
            self.head = Node(value)
            self.tail = self.head
        else:
            self.tail.next = Node(value)
            self.tail = self.tail.next
        self.len += 1
        
    def insert(self,idx,value):
        pointer = self.head
        for i in range(idx-1):
            pointer = pointer.next
        serach = Node(value,pointer.next)
        pointer.next = serach
        self.len += 1
        
    def add(self,value):
        node = Node(value,self.head)
        if self.head == None:
            self.head = node
            self.tail = node
        self.len += 1
        
    def remove(self,idx):
        pointer = self.head
        for i in range(idx-1):
            pointer = pointer.next
        pointer.next = pointer.next.next
        self.len -= 1
        
    def serach(self,value):
        pointer = self.head
        for i in range(self.length()-1):
            if pointer.value == value:
                return True
            else:
                pointer = pointer.next
        return False
            

# ll = UnidirectionalLinkedList()
# ll.add(1)
# pointer = ll.head
# while pointer:
#     print(pointer.value)
#     pointer = pointer.next
# ll.append(2)
# pointer = ll.head
# while pointer:
#     print(pointer.value)
#     pointer = pointer.next
# ll.append(4)
# ll.append(5)
# ll.insert(2,3)
# ll.remove(2)
# ll.add(0)
# print(ll.serach(4))
# print(ll.serach(3))
# pointer = ll.head
# while pointer:
#     print(pointer.value)
#     pointer = pointer.next
# print(ll.len,ll.isempty())

    
    
    