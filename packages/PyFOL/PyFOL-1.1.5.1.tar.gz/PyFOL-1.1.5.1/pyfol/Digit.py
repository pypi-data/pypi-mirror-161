class Digit():
    def __init__(self):
        pass
    
    def plus(self,num1,num2):
        return num1+num2
    
    def minus(self,num1,num2):
        return num1-num2
    
    def multiply(self,num1,num2):
        return num1*num2
    
    def divide(self,num1,num2,reverse=False):
        return num1/num2 if not reverse else num2/num1
    
    def mod(self,num1,num2):
        return num1%num2
        
    def sum(self,lst):
        sumn = 0
        for i in lst:
            sumn += i
        return sumn
    
    def pow(self,base,index):
        return 1 if not index else base * self.pow(base,index-1)
        
    def fac(self,facn):
        return 1 if facn==1 else facn * self.fac(facn-1)
    
# a = digit()
# print(a.pow(3,22))
# print(a.fac(10))

