def find(masterstr,findstr,start=0,end=-1,case_insensitive=False):
    findlst = []
    total = 0
    if case_insensitive:
        masterstr = masterstr.lower()
        findstr = findstr.lower()
    for i in range(start+1,len(masterstr) if end==-1 else end):
        if masterstr[i:i+len(findstr)] == findstr:
            findlst.append(i)
            total += 1
    return findlst,total

# print(find("Hello Python World! Life is short, I use Python!",'e'))
# # ([1, 23, 39], 3)
# print(find("Hello Python World! Life is short, I use Python!",'e',1))
# # ([1, 23, 39], 3)
# print(find("Hello Python World! Life is short, I use Python!",'e',0,38))
# # ([1, 23], 2)
# print(find("Hello Python World! Life is short, I use Python!",'p',0,-1,True))
# # ([6, 41], 2)