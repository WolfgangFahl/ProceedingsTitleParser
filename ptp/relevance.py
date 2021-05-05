'''
Created on 2021-05-31

@author: wf
'''
from collections import Counter
from tabulate import tabulate

class Categorizer(object):
    '''
    categorize some text input
    ''' 
    def __init__(self,categories):
        self.categories=categories
        pass
    
    def categorize(self,text,item):
        results={}
        for category in self.categories:
            tokenSequence=TokenSequence(text)
            result=Categorization(category,tokenSequence)
            if result.matches()>0:
                results[result.name]=result
                result.item=item
        return results
    
class TokenSequence(object):
    
    def __init__(self,text):
        self.words=text.split(' ')
        self.pos=-1
        
    def next(self):
        while self.pos+1<len(self.words):
            self.pos+=1
            yield self.words[self.pos]
        
class Categorization(object):
    
    def __init__(self,category,tokenSequence):
        self.category=category
        self.name=category.name
        self.tokenSequence=tokenSequence
        
    def __str__(self):
        text=f"{self.name}:{self.matchResult}"
        return text

    def matches(self)->list:
        '''
        return how many matches there are
        '''
        self.matchResult=self.category.matches(self.tokenSequence)
        return len(self.matchResult)

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
        
    def matches(self,tokenSequence)->list:
        '''
        match the given tokenSequence
        
        
        '''
        if hasattr(self,"checkMatch") and callable(getattr(self,"checkMatch")):
            matchResult=[]
            for token in tokenSequence.next():
                if self.checkMatch(token):
                    value=self.itemFunc(token)
                    matchResult.append((token,tokenSequence.pos,value))
        return matchResult
    
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
        