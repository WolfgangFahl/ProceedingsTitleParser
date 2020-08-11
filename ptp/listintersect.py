'''
Created on 2020-08-11

@author: wf
'''

class ListOfDict(object):
    '''
    https://stackoverflow.com/questions/33542997/python-intersection-of-2-lists-of-dictionaries/33543164
    '''
    @staticmethod  
    def sortKey(d,key=None):
        ''' get the sort key for the given dict d with the given key
        '''
        if key is None:
            # https://stackoverflow.com/a/60765557/1497139
            return hash(tuple(d.items()))
        else:
            return d[key] 
        
    @staticmethod            
    def intersect(listOfDict1,listOfDict2,key=None):
        '''
        get the  intersection lf the two lists of Dicts by the given key 
        '''
        i1=iter(sorted(listOfDict1, key=lambda k: ListOfDict.sortKey(k, key)))
        i2=iter(sorted(listOfDict2, key=lambda k: ListOfDict.sortKey(k, key)))
        c1=next(i1)
        c2=next(i2)
        lr=[]
        while True:
            try:
                val1=ListOfDict.sortKey(c1,key)
                val2=ListOfDict.sortKey(c2,key)
                if val1<val2:
                    c1=next(i1)
                elif val1>val2:
                    c2=next(i2)
                else:
                    lr.append(c1)
                    c1=next(i1)
                    c2=next(i2)
            except StopIteration:
                break     
        return lr    
        