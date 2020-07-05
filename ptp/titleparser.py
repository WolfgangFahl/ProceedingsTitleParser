'''
Created on 20.06.2020

@author: wf
'''
import yaml
import io
import os
import re
from collections import OrderedDict
from pyparsing import Keyword,Group,Word,OneOrMore,Optional,ParseResults,Regex,ZeroOrMore,alphas, nums, oneOf
from num2words import num2words

class TitleParser(object):
    '''
    parser for Proceeding titles
    '''

    def __init__(self,name=None):
        '''
        Constructor
        '''
        self.name=name
    
    @staticmethod    
    def fromFile(filePath,mode='wikidata'):
        ''' read all lines from the given filePath and return a Parser '''
        tp=TitleParser()
        with open(filePath) as f:
            lines=f.readlines()
        tp.lines=[]
        for line in lines:
            if mode=="wikidata":
                if "@en" in line and "Proceedings of" in line:
                    line=line.strip()
                    parts=line.split('"')
                    subject=parts[0]
                    qref=subject.split("<")[1]
                    qref=qref.split(">")[0]
                    title=parts[1]
                    tp.lines.append({'q': qref, 'title': title})
            elif mode=="dblp":
                m=re.match("<title>(.*)</title>",line)
                if m:
                    title=m.groups()[0]
                    tp.lines.append({'title': title})        
            else:
                title=line.strip()
                tp.lines.append({'title': title})
        return tp   
   
class ProceedingsTitleParser(object):
    ''' a pyparsing based parser for Proceedings Titles supported by a dictionary'''
    year=Regex(r'(19|20)?[0123456789][0123456789]')
    acronymGroup=Optional("("+Group(Word(alphas)+Optional(year))("acronym")+")")
    instance=None
    
    @staticmethod
    def getInstance():
        ''' get a singleton instance of the ProceedingsTitleParser '''
        if ProceedingsTitleParser.instance is None:
            d=ProceedingsTitleParser.getDictionary()
            ProceedingsTitleParser.instance=ProceedingsTitleParser(d)
        return ProceedingsTitleParser.instance
   
    @staticmethod
    def getDictionary():
        path=os.path.dirname(__file__)
        d=Dictionary.fromFile(path+"/../dictionary.yaml")
        return d
        
    def __init__(self, dictionary=None):
        ''' constructor '''
        proc=Keyword("Proceedings") | Keyword("proceedings")
        descWord=~proc + Word(alphas+nums+"™æéç)>/'&—‐") # watch the utf-8 dash! 
        initials="("+OneOrMore(Word(alphas)+".")+")"
        desc=Optional("[")+OneOrMore(descWord|initials)+oneOf(". ? : ( , ; -")
        enumGroup=dictionary.getGroup("enum")
        scopeGroup=dictionary.getGroup("scope")
        eventGroup=dictionary.getGroup("event")
        freqGroup=dictionary.getGroup("frequency")
        yearGroup=dictionary.getGroup("year")
        cityGroup=dictionary.getGroup("city")
        provinceGroup=dictionary.getGroup("province")
        countryGroup=dictionary.getGroup("country")
        eventClause=dictionary.getClause("event")
        monthGroup=dictionary.getGroup("month")
        extractGroup=dictionary.getGroup("extract")
        dateRangeGroup=Group(Optional(Word(nums)+Optional("-"+Word(nums))))("daterange")
        prefixGroup=Group(ZeroOrMore(~oneOf(eventClause)+Word(alphas+nums)))("prefix")
        topicGroup=Group(ZeroOrMore(~oneOf("held on")+Word(alphas+nums+"-&")))("topic")
        part="Part"+oneOf("A B C 1 2 3 4 I II III IV")+"."
        whereAndWhen=Optional(oneOf([".",",","held on"])+dateRangeGroup+monthGroup+dateRangeGroup \
                              +Optional(oneOf(","))+yearGroup \
                              +Optional(oneOf(","))+cityGroup \
                              +Optional(oneOf(","))+provinceGroup \
                              +Optional(oneOf(","))+countryGroup \
                              +Group(Optional(Word(alphas)))("location"))
        self.grammar=Group(ZeroOrMore(desc))("description") \
            +Optional(part) \
            +Optional(oneOf("[ Conference Scientific")) \
            +extractGroup+Optional(oneOf("the The"))+Optional("Official") \
            +proc+"of"+Optional(oneOf("the a an")) \
            +yearGroup \
            +enumGroup \
            +freqGroup \
            +scopeGroup \
            +prefixGroup \
            +Optional(oneOf("Scientific Consensus"))+eventGroup \
            +Optional(oneOf("on of in :")) \
            +topicGroup \
            +ProceedingsTitleParser.acronymGroup \
            +Optional(oneOf("] )")) \
            +whereAndWhen
        pass     
        
class Title(object):
    ''' a single Proceedings title '''
   
    def __init__(self,line,grammar=None,dictionary=None):
        ''' construct me from the given line and dictionary '''
        self.line=line
        if dictionary is not None:
            for blanktoken in dictionary.blankTokens:
                blankless=blanktoken.replace(" ","_")
                line=line.replace(blanktoken,blankless) 
        self.tokens=line.split(' ')
        self.dictionary=dictionary
        self.enum=None
        self.parseResult=None
        self.grammar=grammar
        self.info={}
        self.md=None
        self.event=None
        
    def lookup(self,em):
        ''' look me up with the given event manager '''
        if "acronym" in self.metadata():
            acronym=self.md["acronym"] 
            if acronym is not None:
                self.event=em.lookup(acronym)
                pass
        
    def __str__(self):
        ''' create a string representation of this title '''    
        text=""
        delim=""
        for pitem in self.parseResult:
            if isinstance(pitem,ParseResults):
                text+="%s%s=%s" % (delim,pitem.getName(),pitem)
                delim="\n"
        return text    
    
    def metadata(self):
        ''' extract the metadata of the given title '''
        if self.md is None:
            self.md={}
            for pitem in self.parseResult:
                if isinstance(pitem,ParseResults):
                    value=" ".join(pitem.asList())
                    if value:
                        self.md[pitem.getName()]=value
        return self.md    
        
    def dump(self):
        ''' debug print my parseResult '''
        print (self.parseResult)
        for pitem in self.parseResult:
            if isinstance(pitem,ParseResults):
                print ("%s=%s" % (pitem.getName(),pitem))
            else:     
                print (pitem)   
        pass        
    
    def parse(self):
        for token in self.tokens:
            dtoken=self.dictionary.getToken(token)
            if dtoken is not None:
                if dtoken["type"]=="enum":
                    self.enum=dtoken["value"] 
                self.info[dtoken["type"]]=token
    
    def pyparse(self):
        if self.grammar is not None:
            self.parseResult=self.grammar.parseString(self.line)
                    
        
class Dictionary(object):
    ''' a dictionary to support title parsing '''
    
    def __init__(self):
        self.blankTokens={}
        pass     
    
    def countType(self,tokenType):
        clause=self.getClause(tokenType)
        return len(clause)
    
    def getClause(self,tokenType):
        ''' get a clause to be used for OneOf pyparsing Operator from dictionary for the given type'''
        clause=[]
        for key in self.tokens:
            entry=self.tokens[key]
            if entry["type"]==tokenType:
                clause.append(key)
        return clause
    
    def getGroup(self,tokenType):
        ''' get a group for the given token Type'''
        clause=self.getClause(tokenType)
        group=Group(Optional(oneOf(clause)))(tokenType)
        return group
        
    def getToken(self,token):
        ''' check if this dictionary contains the given token '''
        token=token.replace('_',' ') # restore blank
        for postfix in ['','.',',',':','[',']']:
            search=token.replace(postfix,'')
            if search in self.tokens:
                dtoken=self.tokens[search]
                dtoken["label"]=search
                return dtoken
        return None
    
    @staticmethod
    def fromFile(yamlPath):
        d=Dictionary()
        d.yamlPath=yamlPath
        d.read()
        d.blankHandling()
        return d
    
    def blankHandling(self):
        ''' handle tokens that contain spaces e.g. "Great Britain", "San Francisco", "New York", "United States"'''
        for token in self.tokens:
            if " " in token:
                self.blankTokens[token]=token
        
    def read(self,yamlPath=None):
        ''' read the dictionary from the given yaml path'''
        if yamlPath is None:
            yamlPath=self.yamlPath
        with open(yamlPath, 'r') as stream:
            self.tokens = yaml.safe_load(stream)
        pass
        
    def write(self,yamlPath=None):   
        ''' write the dictionary to a yaml file given py the yamlPath ''' 
        if yamlPath is None:
            yamlPath=self.yamlPath
        sortedTokens=OrderedDict(sorted(self.tokens.items(), key=lambda x: x[1]['type']))    
        self.tokens=dict(sortedTokens)
        # Write YAML file
        with io.open(yamlPath, 'w', encoding='utf8') as outfile:
            yaml.dump(self.tokens, outfile, default_flow_style=False, sort_keys=False,allow_unicode=True)
        with open(yamlPath, 'r') as original: data = original.read()
        comment="""# 
#  Proceedings title dictionary
# 
"""
        with open(yamlPath, 'w') as modified: modified.write(comment + data)    
            
    def add(self,token,tokenType,value=None):
        ''' add or replace the token with the given type to the dictionary '''
        lookup={}
        lookup['type']=tokenType
        if value is not None:
            lookup['value']=value
        self.tokens[token]=lookup
        
    def addEnums(self):
        ''' add enumerations '''
        # https://stackoverflow.com/a/20007730/1497139
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
        for i in range(1,100):
            roman=self.toRoman(i)+"."
            self.add("%d." % i,'enum',i)
            self.add(ordinal(i),'enum',i)
            self.add(roman,'enum',i)
            ordinal4i=num2words(i, to='ordinal')
            self.add(ordinal4i,'enum',i)
            title=ordinal4i.title()
            self.add(title,'enum',i)
            
    def addYears(self):
        for year in range(1960,2030):
            self.add("%d" % year,'year',year)
    
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
