class String():
    def __init__(self,operationstr):
        self.operationstr = operationstr
        
    def setstr(self,nowstr):
        self.operationstr = nowstr
        
    def clearstr(self):
        self.operationstr = ''
        
    def split(self,substr=' ',amount=-1,rm_empty_char=True,splitmode=None,sortword=False,setword=False):
        if self.operationstr[-1] != substr:
            self.operationstr += substr
        split_list = []
        last_search_pos = 0
        num = 0 if amount != -1 else -1
        substr_pos = self.operationstr.find(substr,last_search_pos)
        while substr_pos != -1 and (num < amount if num != -1 else True):
            nowsplitword = self.operationstr[last_search_pos:substr_pos]
            last_search_pos =  substr_pos+len(substr)
            substr_pos =  self.operationstr.find(substr,last_search_pos)
            if num != -1:
                num += 1               
            if rm_empty_char and nowsplitword == '':   
                continue
            if splitmode == None: 
                split_list.append(nowsplitword)
            elif splitmode == 't':
                split_list.append(nowsplitword.title())
            elif splitmode == 'l':
                split_list.append(nowsplitword.lower())
            elif splitmode == 'u':
                split_list.append(nowsplitword.upper())
        if num != -1:
            surplus = self.operationstr[last_search_pos:-1]
            split_list.append(surplus)
        if setword == True:
            split_list = list(set(split_list))
        if sortword == True:
            split_list.sort()
        self.operationstr = self.operationstr[:-1] + ''
        return split_list
    
    def replace(self,replaced_string,replace_string,amount=-1,returntotal=False):
        last_search_pos = 0
        pos_replaced_string = self.operationstr.find(replaced_string,last_search_pos)
        num = 0 if amount != -1 else -1
        total = 0
        while pos_replaced_string != -1 and (num < amount if num != -1 else True):
            self.operationstr = self.operationstr[:pos_replaced_string] + replace_string + self.operationstr[pos_replaced_string+len(replaced_string):]
            
            last_search_pos =  pos_replaced_string+len(replace_string)
            pos_replaced_string =  self.operationstr.find(replaced_string,last_search_pos)
            if num != -1:
                num += 1    
            if returntotal:
                total += 1
        if returntotal:
            return self.operationstr,total
        elif not returntotal:
            return self.operationstr
        
    def find(self,findstr,start=0,end=-1,case_insensitive=False):
        findlst = []
        total = 0
        if case_insensitive:
            self.operationstr = self.operationstr.lower()
            findstr = findstr.lower()
        for i in range(start+1,len(self.operationstr) if end==-1 else end):
            if self.operationstr[i:i+len(findstr)] == findstr:
                findlst.append(i)
                total += 1
        return findlst,total
    
    def append(self,appendstr):
        self.operationstr += appendstr
        
    def insert(self,pos,insertstr):
        self.operationstr = self.operationstr[:pos] + insertstr + self.operationstr[pos:]
        
    def add(self,addstr):
        self.operationstr = addstr + self.operationstr
        
    def delete(self,pos,len=1):
        self.operationstr = self.operationstr[:pos] + self.operationstr[pos+len:]
            
    def pop(self,len=1):
        if len > 1:
            pop = self.operationstr[-1-len:-1]
            self.operationstr = self.operationstr[:-1-len]   
            return pop
        elif len==1:
            pop = self.operationstr[-1]
            self.operationstr = self.operationstr[:-1]
            return pop
        
    def count(self,countstr):
        return self.find(countstr)[1]
    
    def reverse(self):
        newstr = ''
        i = len(self.operationstr)-1
        while i != -1:
            newstr += self.operationstr[i]
            i -= 1
        self.operationstr = newstr
        
    def chartotal(self,start=0,end=-1):
        sum = 0
        for i in self.operationstr[start:len(self.operationstr) if end==-1 else end]:
            sum += ord(i)
        return sum
    
# strobj = string("Hello Python World")

# print(strobj.split())
# print()

# print(strobj.replace('l',"L"))
# print()

# print(strobj.find('o'))
# print()

# strobj.append('!')
# print(strobj.operationstr)
# print()

# strobj.insert(1,"*")
# print(strobj.operationstr)
# print()

# strobj.add("*")
# print(strobj.operationstr)
# print()

# strobj.delete(1,1)
# print(strobj.operationstr)
# print()

# print(strobj.pop())
# print(strobj.operationstr)
# print()

# print(strobj.pop(2))
# print(strobj.operationstr)
# print()

# print(strobj.chartotal())
# print()

# strobj.setstr("火心是个大傻狗")
# print(strobj.operationstr)
# print()

# strobj.reverse()
# print(strobj.operationstr)
# print()

# strobj.clearstr()
# print(strobj.operationstr)

