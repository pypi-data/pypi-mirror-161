def sum(lst,start=0,end=-1):
    sum = 0
    for i in lst[start:len(lst) if end==-1 else end]:
        sum += i
    return sum

def sumstr(lst,start=0,end=-1,mode='s+'):
    if mode == 's+':
        sum = ''
        for i in lst[start:len(lst) if end==-1 else end]:
            sum += i
        return sum
    elif mode == 'sd+':
        sum = 0
        for i in lst[start:len(lst) if end==-1 else end]:
            sum += ord(i)
        return sum
    
# print(sum([1,2,3],0,2))
# print(sum([1.2,2.3,3.4],0,2))
# print(sumstr(['a','b','c'],0,2))
# print(sumstr(['a','b','c'],0,2,'sd+'))