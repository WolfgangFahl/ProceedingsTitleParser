'''
Created on 2021-05-31

@author: wf
'''
from collections import Counter
from tabulate import tabulate

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
        
    def add(self,item):
        '''
        add the given item with the given value
        '''
        value=self.itemFunc(item)
        if value in self.items:
            self.items[value].append(item)
        else:
            self.items[value]=[item]
        self.counter[value]+=1
        
    def matches(self):
        pass
        
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
        