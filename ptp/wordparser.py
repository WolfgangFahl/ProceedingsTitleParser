'''
Created on 2020-04-09

@author: wf
'''

class CorpusWordParser():
    def __init__(self):
        pass
    
    '''
    parse the given records
    '''
    def parse(self,records):
        print("parsing %d titles" % len(records))
        lens=[]
        for record in records:
            title=record['title']
            wp=WordParser()
            l=wp.parse(title)
            lens.append(l)
        print("found %d length values" % len(lens))  
        return lens  

class WordParser(object):
    '''
    Word base parser
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def parse(self,title):
        words=title.split(' ')
        return (len(words))