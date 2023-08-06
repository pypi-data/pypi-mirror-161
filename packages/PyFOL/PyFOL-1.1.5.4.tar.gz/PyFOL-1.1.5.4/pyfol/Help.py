class Help():
    def __init__(self,helpobject):
        self.ho = helpobject
        self.helpjudge()
        
    def helpjudge(self):
        import pyfol as pfl
        self.ho = pfl.String(self.ho).split("/")
        if self.ho[0] == 'String':
            if self.ho[1] == 'setstr':
                self.Hsetstr()
            elif self.ho[1] == 'clearstr':
                self.Hclearstr()
            elif self.ho[1] == 'split':
                self.Hsplit()
            elif self.ho[1] == 'replace':
                self.Hreplace()
            elif self.ho[1] == 'find':
                self.Hfind()
            elif self.ho[1] == 'append':
                self.Happend()
            elif self.ho[1] == 'insert':
                self.Hinsert()
            elif self.ho[1] == 'add':
                self.Hadd()
            elif self.ho[1] == 'delete':
                self.Hdelete()
            elif self.ho[1] == 'pop':
                self.Hpop()
            elif self.ho[1] == 'count':
                self.Hcount()
            elif self.ho[1] == 'reverse':
                self.Hreverse()
            elif self.ho[1] == 'chartotal':
                self.Hchartotal()
                
    def Hsetstr(self):
        return "Setstr is a function that resets a string to a new string"
        
    def Hclearstr(self):
        return "Clearstr is a function that resets a string to an empty string"
        
    def Hsplit(self):
        return "Split is a function that splits a string"
    
    def Hreplace(self):
        return "Replace is a function that replaces a substring of a string"
        
    def Hfind(self):
        return "Find is a function that finds a substring in a string"
    
    def Happend(self):
        return "Append is a function that adds a new string (or character) to the end of a string"
        
    def Hinsert(self):
        return "Insert is a function that adds a new string (or character) at a specific position of a string"
        
    def Hadd(self):
        return "Add is a function that adds a new string (or character) at the beginning of a string"
        
    def Hdelete(self):
        return "Delete is a function that deletes a certain length of string (or character) at a specific position of a string"
        
    def Hpop(self):
        return "Pop is a function that deletes and pops a certain length of string (or character) at the end of a string"
        
    def Hcount(self):
        return "Count is a function that counts the number of occurrences of substrings in a string"
        
    def Hreverse(self):
        return "Reverse is a function that reverses a string as a whole"
    
    def Hchartotal(self):
        return "Chartotal is a function that counts the ASCII encoding of each character in the function of overall inversion of a string"
        