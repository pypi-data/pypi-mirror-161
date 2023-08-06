def split(masterstr,substr=' ',amount=-1,rm_empty_char=True,splitmode=None,sortword=False,setword=False,dirty_filter=False):
    import better_profanity
    if masterstr[-1] != substr:
        masterstr += substr
    split_list = []
    last_search_pos = 0
    num = 0 if amount != -1 else -1
    substr_pos = masterstr.find(substr,last_search_pos)
    while substr_pos != -1 and (num < amount if num != -1 else True):
        nowsplitword = masterstr[last_search_pos:substr_pos]
        last_search_pos =  substr_pos+len(substr)
        substr_pos =  masterstr.find(substr,last_search_pos)
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
        surplus = masterstr[last_search_pos:-1]
        split_list.append(surplus)
    if setword == True:
        split_list = list(set(split_list))
    if sortword == True:
        split_list.sort()
    if dirty_filter:
        for i in range(len(split_list)):
            if better_profanity.profanity.contains_profanity(split_list[i]):
                split_list[i] = better_profanity.profanity.censor(split_list[i])
    return split_list
    
# str1 = "Hello Python World ! Life is short , I use Python !"
# str2 = "Hello_Python_World_!_Life_is_short_,_I_use_Python_!"
# str3 = "Hello!Python!World!!Life!is!short!,!!I use Python!!"
# str4 = "Python is a shit and a bitch"

# print(split(str1))
# # ['Hello', 'Python', 'World', '!', 'Life', 'is', 'short', ',', 'I', 'use', 'Python', '!']

# print(split(str2,'_'))
# # ['Hello', 'Python', 'World', '!', 'Life', 'is', 'short', ',', 'I', 'use', 'Python', '!']

# print(split(str1,amount=6))
# # ['Hello', 'Python', 'World', '!', 'Life', 'is', 'short , I use Python !']

# print(split(str1,splitmode='t'))
# print(split(str1,splitmode='l'))
# print(split(str1,splitmode='u'))
# # ['Hello', 'Python', 'World', '!', 'Life', 'Is', 'Short', ',', 'I', 'Use', 'Python', '!']
# # ['hello', 'python', 'world', '!', 'life', 'is', 'short', ',', 'i', 'use', 'python', '!']
# # ['HELLO', 'PYTHON', 'WORLD', '!', 'LIFE', 'IS', 'SHORT', ',', 'I', 'USE', 'PYTHON', '!']

# print(split(str3,'!',rm_empty_char=False))
# # ['Hello', 'Python', 'World', '', 'Life', 'is', 'short', ',', '', 'I use Python', '']

# print(split(str1,sortword=True))
# # ['!', '!', ',', 'Hello', 'I', 'Life', 'Python', 'Python', 'World', 'is', 'short', 'use']

# print(split(str1,setword=True))
# # ['World', 'Python', 'I', 'is', 'use', 'short', ',', 'Hello', 'Life', '!']

# print(split(str4,dirty_filter=True))
# # ['Python', 'is', 'a', '****', 'and', 'a', '****']