def replace(masterstr,replaced_string,replace_string,amount=-1,returntotal=False,dirty_filter=False):
    import better_profanity
    last_search_pos = 0
    pos_replaced_string = masterstr.find(replaced_string,last_search_pos)
    num = 0 if amount != -1 else -1
    total = 0
    while pos_replaced_string != -1 and (num < amount if num != -1 else True):
        masterstr = masterstr[:pos_replaced_string] + replace_string + masterstr[pos_replaced_string+len(replaced_string):]
        
        last_search_pos =  pos_replaced_string+len(replace_string)
        pos_replaced_string =  masterstr.find(replaced_string,last_search_pos)
        if num != -1:
            num += 1    
        if returntotal:
            total += 1
    if dirty_filter:
        masterstr = better_profanity.profanity.censor(masterstr)
    if returntotal:
        return masterstr,total
    elif not returntotal:
        return masterstr

# str = "Hello Python World! Life is short, I use Python!"  
# str2 = "Python is a shit and a bitch"
# print(replace(str,'Python','C++'))
# # Hello C++ World! Life is short, I use C++!

# print(replace(str,'Python','Java',returntotal=True))
# # ('Hello Java World! Life is short, I use Java!', 2)

# print(replace(str2,'Python','Bitch',dirty_filter=True))
# # **** is a **** and a ****