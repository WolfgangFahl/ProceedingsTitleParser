'''
Created on 2021-05-31

@author: wf
'''
from collections import Counter
from tabulate import tabulate

class Tokenizer(object):
    '''
    categorize some text input
    ''' 
    def __init__(self,categories):
        self.categories=categories
        for category in categories:
            for neededFunc in ["checkMatch","itemFunc"]:
                hasNeededFunc=hasattr(category,neededFunc) and callable(getattr(category,neededFunc))
                if not hasNeededFunc:
                    raise Exception(f"category {category.name} has no {neededFunc} function")
        pass
    
    def tokenize(self,text,item):
        '''
        tokenize the given text for the given item
        '''
        tokenSequence=TokenSequence(text)
        tokenSequence.match(self.categories,item)
        return tokenSequence
        
class TokenSequence(object):
    '''
    a sequence of tokens
    '''
    
    def __init__(self,text,separator=' '):
        self.words=text.split(separator)
        self.pos=-1
        self.matchResults=[]
        
    def next(self):
        while self.pos+1<len(self.words):
            self.pos+=1
            yield self.words[self.pos]
            
    def match(self,categories:list,item:object)->list:
        '''
        match me for the given categories
        
        '''
        self.item=item
        for tokenStr in self.next():
            for category in categories:
                if category.checkMatch(tokenStr):
                    token=Token(category,self,self.pos,tokenStr,item)
                    self.matchResults.append(token)
        return self.matchResults
    
    def __str__(self):
        text=f"{self.name}:{self.matchResults}"
        return text
        
        
class Token(object):
    '''
    a single categorized token
    '''
    
    def __init__(self,category,tokenSequence,pos,tokenStr,item):
        self.category=category
        self.name=category.name
        self.tokenSequence=tokenSequence
        self.pos=pos
        self.tokenStr=tokenStr
        self.value=category.add(item,tokenStr)
       
        
class Category(object):
    '''
    I am a category
    '''

    def __init__(self, name, itemFunc):
        '''
        Constructor
        '''
        self.name=name
        self.items={}
        self.itemFunc=itemFunc
        self.counter=Counter()
        self.subCategories={}
        
    def addCategory(self,category):
        self.subCategory[category.name]=category
        
    def add(self,item,propValue):
        '''
        add the given item with the given value
        '''
        value=self.itemFunc(propValue)
        if value in self.items:
            self.items[value].append(item)
        else:
            self.items[value]=[item]
        self.counter[value]+=1
        return value
        
   
    def mostCommonTable(self,headers=["#","key","count","%"],tablefmt='pretty',limit=50):
        '''
        get the most common Table
        '''
        bins=len(self.counter.keys())
        limit=min(bins,limit)
        total=sum(self.counter.values())
        binTable=[("total",bins,total)]
        for i,bintuple in enumerate(self.counter.most_common(limit)):
            key,count=bintuple
            binTable.append((i+1,key,count,count/total*100.0))
        
        table=tabulate(binTable,headers=headers,tablefmt=tablefmt,floatfmt=".2f")
        return table
        