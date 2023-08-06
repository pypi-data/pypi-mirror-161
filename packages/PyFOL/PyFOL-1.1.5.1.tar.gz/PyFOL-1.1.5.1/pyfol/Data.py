class Data():
    def __init__(self):
        pass
    
    def swap(self,var1,var2):
        return var2,var1
    
    def max(self,num1,num2):
        return num1 if num1>num2 else num2
    
    def min(self,num1,num2):
        return num1 if num1<num2 else num2
    
    def maxlst(self,lst):
        return max(lst)
    
    def minlst(self,lst):
        return min(lst)
    
    def avg(self,lst):
        sum = 0
        for i in lst:
            sum += i
        return sum/len(lst)
    
    def gcd(self,num1,num2):
        gcdlst = []
        for i in range(1,self.min(num1,num2)+1):
            if num1 % i == 0 and num2 % i == 0:
                gcdlst.append(i)
        return self.maxlst(gcdlst)
    
    def lcm(self,num1,num2):
        for i in range(self.max(num1,num2),num1*num2+1):
            if i % num1 ==0 and i % num2 ==0:
                return i
            
    def randms(self,seed):
        seed **= 2
        return int(str(seed)[1:5])
    
# dat = Data()
# print(dat.gcd(319,377))
# print(dat.lcm(704,2048))
    
    