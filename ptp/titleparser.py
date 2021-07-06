'''
Created on 2020-06-20

@author: wf
'''
import yaml
import io
import json
import jsons
import os
import re
from collections import OrderedDict
from pyparsing import Keyword,Group,Word,OneOrMore,Optional,ParseResults,Regex,ZeroOrMore,alphas, nums, oneOf
# wait for version 3
#from pyparsing.diagram import to_railroad, railroad_to_html
from num2words import num2words
from collections import Counter
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from ptp.event import EventManager
from lodstorage.plot import Plot


class TitleParser(object):
    '''
    parser for Proceeding titles
    '''

    def __init__(self,name=None,lookup=None,ptp=None,dictionary=None,ems=None):
        '''
        Constructor
        '''
        self.name=name
        self.lookup=lookup
        self.ptp=ptp
        if dictionary is None and ptp is not None:
            ptpdictionary=ptp.getDictionary()
            if ptpdictionary is not None:
                self.dictionary=ptpdictionary
        else:
            self.dictionary=dictionary
        self.ems=ems
        self.records=[]
        
    @staticmethod
    def getDefault(name=None):
        ptp=ProceedingsTitleParser.getInstance()
        tp=TitleParser(name,ptp=ptp)
        return tp

    def parseAll(self):
        ''' get parse result with the given proceedings title parser, entity manager and list of titles '''
        errs=[]
        result=[]
        tc=Counter()
        for record in self.records:
            eventTitle=record['title']
            if eventTitle is not None:
                title=Title(eventTitle,self.ptp.grammar,dictionary=self.dictionary)
                for key in ['source','proceedingsUrl']:
                    if key in record:
                        title.info[key]=record[key]
                if 'eventId' in record:
                    title.info['eventId']=record['eventId']
                try:
                    notfound=title.parse()
                    title.pyparse()
                    tc["success"]+=1
                except Exception as ex:
                    tc["fail"]+=1
                    errs.append(ex)
                if self.ems is not None:    
                    title.lookup(self.ems,notfound)
                result.append(title)
        return tc,errs,result

    def asJson(self,result):
        '''convert the given result to JSON '''
        events=[]
        for title in result:
            events.extend(title.events)
        jsonResult={"count": len(events), "events": events}
        jsons.suppress_warnings()
        jsonText=jsons.dumps(jsonResult,indent=4,sort_keys=True)
        return jsonText
    
    def getEventDicts(self,result):
        '''
        get the results as a list of event dicts
        '''
        events=[]
        for title in result:
            for event in title.events:
                events.append(event.__dict__)
        return events        
                
    def asXml(self,result,pretty=True):
        ''' convert result to XML'''
        events=self.getEventDicts(result)        
        item_name = lambda x: "event"        
        xml=dicttoxml(events, custom_root='events',item_func=item_name, attr_type=False)
        if pretty:
            dom=parseString(xml)
            prettyXml=dom.toprettyxml()
        else:
            prettyXml=xml    
        return prettyXml
    
    def asWikiSon(self,result):
        '''
        return the given result in WikiSon format
        '''
        events=self.getEventDicts(result)   
        return EventManager.asWikiSon(events)
    
    def asCsv(self,result):
        events=self.getEventDicts(result)  
        return EventManager.asCsv(events)         
    
    def fromLines(self,lines,mode='wikidata',clear=True):
        ''' get my records from the given lines using the given mode '''
        if clear:
            self.records=[]
        ''' add records from the given lines '''
        for line in lines:
            if mode=="wikidata":
                if "@en" in line and "Proceedings of" in line:
                    line=line.strip()
                    parts=line.split('"')
                    subject=parts[0]
                    qref=subject.split("<")[1]
                    qref=qref.split(">")[0]
                    title=parts[1]
                    self.records.append({'source':'wikidata','eventId': qref, 'title': title})
            elif mode=="dblp":
                m=re.match("<title>(.*)</title>",line)
                if m:
                    title=m.groups()[0]
                    self.records.append({'title': title})
            elif mode=="CEUR-WS":
                parts=line.strip().split("|")
                title=parts[0]
                vol=None
                partlen=len(parts)
                if partlen>1:
                    idpart=parts[partlen-1]
                    # id=Vol-2534
                    vol=idpart.split("=")[1]
                self.records.append({'source':'CEUR-WS','eventId': vol,'title': title})
            elif mode=="line":
                title=line.strip()
                # DOI
                # https://www.crossref.org/blog/dois-and-matching-regular-expressions/
                if re.match(r'^10.\d{4,9}\/.*',title):
                    if self.lookup:
                        record=self.lookup.extractFromDOI(title)
                        self.records.append(record)
                # URL
                elif title.startswith('http'):
                    if self.lookup:
                        record=self.lookup.extractFromUrl(title)
                        if record is not None:
                            self.records.append(record)
                else:
                    self.records.append({'source':'line', 'title': title})
            else:
                raise Exception("unknown mode %s" % (mode))

    def fromFile(self,filePath,mode='wikidata'):
        ''' read all lines from the given filePath and return a Parser '''
        with open(filePath) as f:
            lines=f.readlines()
        self.fromLines(lines,mode)

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

    def __init__(self, dictionary):
        ''' constructor 
        '''
        self.dictionary=dictionary
        proc=Keyword("Proceedings") | Keyword("proceedings")
        descWord=~proc + Word(alphas+nums+"™æéç)>/'&—‐") # watch the utf-8 dash!
        initials="("+OneOrMore(Word(alphas)+".")+")"
        desc=Optional("[")+OneOrMore(descWord|initials)+oneOf(". ? : ( , ; -")
        enumGroup=dictionary.getGroup("enum")
        scopeGroup=dictionary.getGroup("scope")
        eventGroup=dictionary.getGroup("eventType")
        freqGroup=dictionary.getGroup("frequency")
        yearGroup=dictionary.getGroup("year")
        cityGroup=dictionary.getGroup("city")
        provinceGroup=dictionary.getGroup("province")
        countryGroup=dictionary.getGroup("country")
        eventClause=dictionary.getClause("eventType")
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
    special=['.',',',':','[',']','"','(',')']

    def __init__(self,line,grammar=None,dictionary=None):
        ''' construct me from the given line and dictionary '''
        self.line=line
        if line and dictionary is not None:
            for blanktoken in dictionary.blankTokens:
                blankless=blanktoken.replace(" ","_")
                line=line.replace(blanktoken,blankless)
        if self.line:
            self.tokens=re.split(r'[ ,.()"\[\]]',line)
        else:
            self.tokens=[]
        self.dictionary=dictionary
        self.enum=None
        self.parseResult=None
        self.grammar=grammar
        self.info={'title':line}
        self.md=None
        self.events=[]

    def addSearchResults(self,ems,search):
        ''' add search results from the given event managers with the given search keyword
        FIXME: a search for e.g CA 2008 does not make much sense since the word CA is ambigous and
        probably a province CA=California and not an Acronym
        '''
        for em in ems:
            events=em.lookup(search)
            for event in events:
                event.foundBy=search
                self.events=self.events+events

    def lookup(self,ems,wordList=None):
        ''' look me up with the given event manager use my acronym or optionally a list of Words'''
        if "acronym" in self.metadata():
            acronym=self.md["acronym"]
            if acronym is not None:
                self.addSearchResults(ems, acronym)
        # last resort search
        if len(self.events)==0:
            if wordList is not None and "year" in self.info:
                year=self.info["year"]
                for word in wordList:
                    self.addSearchResults(ems, word+" "+year)

    def __str__(self):
        ''' create a string representation of this title '''
        text=""
        delim=""
        if self.parseResult is not None:
            for pitem in self.parseResult:
                if isinstance(pitem,ParseResults):
                    text+="%s%s=%s" % (delim,pitem.getName(),pitem)
                    delim="\n"
        return text
    
    def hasUrl(self):
        result='proceedingsUrl' in self.info or 'url' in self.info
        return result
    
    def getUrl(self):
        for key in ['proceedingsUrl','url']:
            if key in self.info:
                return self.info[key]
        return None
 
    def asJson(self):
        events=[]
        events.extend(self.events)
        jsonResult={"count": len(self.events), "events": events}
        jsonText=json.dumps(jsonResult,indent=4,sort_keys=True)
        return jsonText
        
    def metadata(self):
        ''' extract the metadata of the given title '''
        if self.md is None:
            # initialize with None values
            self.md={
                'enum': None, 
                'description': None,
                'delimiter': None,
                'daterange': None,
                'eventType': None,
				'extract': None,
                'field': None,
                'frequency': None,
                'location': None,
                'lookupAcronym': None,
                'month': None,
                'ordinal': None,
                'organization': None,
                'prefix': None,
                'province': None,
                'publish': None,
                'scope': None,
                'syntax': None,
                'topic': None,
                'year': None
            }
            if self.parseResult is not None:
                for pitem in self.parseResult:
                    if isinstance(pitem,ParseResults):
                        value=" ".join(pitem.asList())
                        if value:
                            name=pitem.getName()
                            self.md[name]=value
            if self.info is not None:
                for name in self.info:
                    value=self.info[name]
                    # value is not None per definition
                    # mdValue might be None
                    if (not name in self.md) or (self.md[name] is None):
                        self.md[name]=value
            if self.md['year'] is not None:
                self.md['year']=int(self.md['year'])            
        return self.md
    
    def metadataDump(self):
        md=self.metadata()
        jsonText=json.dumps(md,indent=4,sort_keys=True)
        return jsonText
        

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
        '''
        parse with dictionary lookup
        '''
        self.notfound=[]
        for token in self.tokens:
            dtoken=self.dictionary.getToken(token)
            # if ther is a dictionary result
            if dtoken is not None:
                # for the kind e.g. enum, country, city ...
                lookup=dtoken["type"]
                # do not set same token e.g. enum twice
                if not lookup in token:
                    if lookup=="enum":
                        self.info['ordinal']=dtoken["value"]
                    # set the value for the token
                    self.info[lookup]=token
            else:
                self.notfound.append(self.dictionary.searchToken(token))
        return self.notfound

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

    def searchToken(self,token):
        ''' replace the given token with it's search equivalent by removing special chars '''
        search=token
        for special in Title.special:
            search=token.replace(special,'')
        return search

    def getToken(self,token):
        ''' check if this dictionary contains the given token '''
        token=token.replace('_',' ') # restore blank
        search=self.searchToken(token)
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

class TokenStatistics(object):
    '''
    keep track of token/wordcount
    '''
    def __init__(self,name,dictionary):
        self.name=name
        self.tc=Counter()
        self.typeCounters={}
        self.kc=Counter()
        self.known=0
        self.total=0
        self.recordCount=0
        self.tclist=[]
        self.d=dictionary
        pass

    def addToken(self,token,dtoken):
        self.total+=1
        if dtoken is None:
            self.tc[token]+=1
        else: 
            self.known+=1
            self.kc[token]+=1
            tokenType=dtoken["type"]
            if tokenType in self.typeCounters:
                typeCounter=self.typeCounters[tokenType]
            else:
                typeCounter=Counter()
                self.typeCounters[tokenType]=typeCounter
            label=dtoken["label"]    
            typeCounter[label]+=1        
    
    def addTokenCount(self,tokenCount):
        self.recordCount+=1
        self.tclist.append(tokenCount)
        
    def showHistogramm(self,title):
        plot=Plot(self.tclist,title)
        plot.hist(mode="save")
        
    def showMostCommon(self,limit):
        print(self.tc.most_common(limit))   
        print(self.kc.most_common(limit))    
        
    def showTypeTable(self):
        ''' show the table of found types '''
 
        for tokenType in self.typeCounters:
            typeCounter=self.typeCounters[tokenType]
            print ("%s: %s" % (tokenType,typeCounter.most_common(5)))
            
        print("titles: %d found words: %d of %d %5.1f%%" % (self.recordCount,self.known,self.total,self.known/self.total*100))   
        self.showWikiTable()
        self.showLaTexTable()
        
    def showLaTexTable(self):
        tableStart="""\\begin{table}
\caption{%s}
\label{tab:%s}
\\begin{tabular}{l|r|r|r|l} 
type & entries & found & \\%% & most common examples: count \\\\ \hline """
        tableEnd="""
\end{tabular}
\end{table}"""
        row="%s & %d & %d & (%5.1f\\%%) & %s"
        rowDelim="\\\\"
        self.showGenericTable(tableStart=tableStart,tableEnd=tableEnd, rowDelim=rowDelim,row=row)
        
    def showWikiTable(self):
        tableStart="""
== %s ==
<!-- %s-->
{| class="wikitable"
|-
! type !! entries !! found !! most common examples: count"""
        rowDelim="|-\n"
        row="|%s || %d || %d (%5.1f%%) || %s"
        tableEnd="|}"
        self.showGenericTable(tableStart=tableStart,tableEnd=tableEnd,rowDelim=rowDelim,row=row)
        
    def showGenericTable(self,tableStart,tableEnd,rowDelim,row):     
        '''
        show a generic table
        ''' 
        print (tableStart % (self.name,self.name))
        for tokenType in sorted(self.typeCounters):
            typeCounter=self.typeCounters[tokenType]
            print (rowDelim,end='')
            mc=typeCounter.most_common(5)
            mcs=""
            delim=""
            for item,count in mc:
                mcs=mcs+"%s%s: %d" % (delim,item,count)
                delim=", "
            typeTotal=sum(typeCounter.values())    
            print (row % (tokenType,self.d.countType(tokenType),typeTotal,typeTotal/self.recordCount*100,mcs))
        print (tableEnd)   