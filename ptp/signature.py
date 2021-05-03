'''
Created on 2021-05-03

Proceedings Title signature elements
@author: wf
'''
from ptp.relevance import Category

class OrdinalCategory(Category):
    '''
    I am the category for ordinals
    '''

    def __init__(self,maxOrdinal=150):
        '''
        Constructor
        '''
        self.maxOrdinal=maxOrdinal
        self.prepareLookup()
        super().__init__("Ordinal",itemFunc=lambda event:self.getOrdinal(event))
        
    def getOrdinal(self,event):
        for word in event.title.split(' '):
            if word in self.lookup:
                return self.lookup[word]
        return None
        
    def prepareLookup(self):
        self.lookup={}
        # https://stackoverflow.com/a/20007730/1497139
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
        for i in range(1,self.maxOrdinal):
            # standard decimal ordinal 1., 2., 3. 
            self.lookup[f"{i}."]=i
            # text ordinal 1st, 2nd, 3rd
            self.lookup[f"{ordinal(i)}"]=i
            # roman
            self.lookup[f"{self.toRoman(i)}."]=i
            
    
    def toRoman(self,number):
        ''' https://stackoverflow.com/a/11749642/1497139 '''
        if (number < 0) or (number > 3999):
            raise Exception("number needs to be between 1 and 3999")
        if (number < 1): return ""
        if (number >= 1000): return "M" + self.self.toRoman(number - 1000)
        if (number >= 900): return "CM" + self.toRoman(number - 900)
        if (number >= 500): return "D" + self.toRoman(number - 500)
        if (number >= 400): return "CD" + self.toRoman(number - 400)
        if (number >= 100): return "C" + self.toRoman(number - 100)
        if (number >= 90): return "XC" + self.toRoman(number - 90)
        if (number >= 50): return "L" + self.toRoman(number - 50)
        if (number >= 40): return "XL" + self.toRoman(number - 40)
        if (number >= 10): return "X" + self.toRoman(number - 10)
        if (number >= 9): return "IX" + self.toRoman(number - 9)
        if (number >= 5): return "V" + self.toRoman(number - 5)
        if (number >= 4): return "IV" + self.toRoman(number - 4)
        if (number >= 1): return "I" + self.toRoman(number - 1)
        