'''
Created on 2020-06-20

@author: wf
'''
import unittest
from ptp.titleparser import TitleParser, Title, \
    ProceedingsTitleParser, TokenStatistics
from collections import Counter
from ptp.location import CountryManager

import networkx as nx
import os
from ptp.openresearch import OpenResearch
from ptp.lookup import Lookup


class TestProceedingsTitleParser(unittest.TestCase):
    """ test the parser for Proceedings titles"""

    def setUp(self):
        self.debug=False
        path=os.path.dirname(__file__)
        self.titlesdir=path+"/../sampledata/"
        pass

    def tearDown(self):
        pass
    
    def getTitleParser(self,name,expectedRecords,mode="wikidata"):
        ''' get a title parser for the given name '''
        titleFile=self.titlesdir+name
        tp=TitleParser(name=name)
        tp.fromFile(titleFile,mode)
        print ("%6d records found at least %6d expected" % (len(tp.records),expectedRecords))
        self.assertTrue(expectedRecords<=len(tp.records))
        return tp 
    
    def getParser(self):
        '''
        get the ProceedingsTitleParser singleton instance
        '''
        return ProceedingsTitleParser.getInstance()
       
    def tryParse(self,line,parser,tc,eventId=None,doprint=False):
        """ try parsing the given line and return the title"""
        title=Title(line,parser.grammar,dictionary=parser.dictionary)
        if eventId is not None and self.debug:
            print ("eventId=%s" % (eventId)) 
        if doprint:    
            print (line)
        try: 
            title.pyparse()
            if self.debug:
                title.dump()
            metadata=title.metadata()
            for key in metadata.keys():
                value=metadata[key]
                if value is not None:
                    tc[key]+=1
            if doprint:    
                print (metadata)    
            tc["success"]+=1
            return title
        except Exception as ex:
            tc["fail"]+=1
            if self.debug:
                print("%s:%s" %(eventId,line))
                print (ex)
            return None
        
    def testExamples(self):
        ''' test specific examples for parsing success '''
        titlelines=[
            "Computer-assisted modeling of receptor-ligand interaction. Theoretical aspects and applications to drug design. Proceedings of the 1988 OHOLO Conference. Eilat, Israel, April 24-28, 1988",
            "Advances in chronic kidney disease 2009. Proceedings of the 11th International Conference on Dialysis. January 28-30, 2009. Las Vegas, Nevada, USA",
            "Nutrition in Clinical Management of HIV-Infected Adolescents (>14 y old) and Adults including Pregnant and Lactating Women: What Do We Know, What Can We Do, and Where Do We Go from Here? Proceedings of a conference held in Washington, DC, July 26-28",
            "Abstracts of the Official Proceedings of the 11th Annual Meeting of the American Society of Breast Surgeons. April 28-May 2, 2010. Las Vegas, Nevada, USA",
            "Old and New Dopamine Agonists in Parkinson's Disease: a Reappraisal. Proceedings of the LIMPE Seminar, 26-28 February, Pisa, Italy, 2009",
            "The Proceedings of the 97th Tohoku Regional Meeting of the Japanese Society of Neurology",
            "Subchondral Pathology: Proceedings of the International Consensus Meeting on Cartilage Repair of the Ankle",
            "Scientific Proceedings of the Twenty-seventh Annual Meeting of the American Association of Pathologists and Bacteriologists",
            "Bulletins et Mémoires de la Société Française d'Ophtalmologie: Proceedings of 1980 Congress",
            "British Pædiatric Association: Proceedings of the First Annual General Meeting",
            "Advances in Medical Computing (Proceedings of the 3rd International Symposium on Computers in Medicine)",
            "Red Drum Aquaculture, Proceedings of a Symposium on the Culture of Red Drum and Other Warm Water Fishes",
            "A summary of the Proceedings of the Twelfth International Symposium on the Neurobiology and Neuroendocrinology of Aging, Bregenz, Austria July 27-August 1, 2014.",
            "[Update on vaccine research. Proceedings of the 15th annual conference on vaccine research organized by the National Foundation for Infectious Diseases].",
            "Very broad Markush claims; a solution or a problem? Proceedings of a round-table discussion held on August 29, 1990.",
            "Abstracts From the Proceedings of the 2015 Annual Meeting of the Clerkship Directors of Internal Medicine (CDIM).",
            "Christo Deltshev & Pavel Stoev (eds) (2006): European Arachnology 2005, Acta zoologica bulgaria, Suppl. No. 1; Proceedings of the 22nd European Colloquium of Arachnology, Blagoevgrad, Bulgaria, 1-6 August 2005",
            "(L.) Bricault and (M.J.) Versluys Eds Power, Politics, and the Cults of Isis: Proceedings of the Vth International Conference of Isis Studies (Religions in the Graeco-Roman World 180). Leiden: Brill, 2014. Pp. xvii + 364. €139/$180. 9789004277182",
            "Kunaitupii: Coming Together on Native Sacred Sites—Their Sacredness, Conservation and Interpretation. Brian O. K. Reeves and Margaret A. Kennedy, editors. Proceedings of the First Joint Meeting of the Archaeological Society of Alberta and the Monta",
            "Jan Apel and Kjel Knutsson: Skilled Production and Social Reproduction. Aspects of Traditional Stone‐Tool Technologies. Proceedings of a Symposium in Uppsala, August 20–24, 2003",
            "Developing ambient intelligence - proceedings of the first international conference on ambient intelligence developments.",
            #"Sea Lice 2003 - Proceedings of the sixth international conference on sea lice biology and control"
            #'Tagungsband des 17. Workshops "Software Engineering im Unterricht der Hochschulen" 2020 (SEUH 2020),Innsbruck, Österreich, 26. - 27.02.2020.'
            ]
        parser=self.getParser()
        tc=Counter()
        for line in titlelines:
            self.tryParse(line, parser, tc)
        self.assertEqual(tc["success"],len(titlelines))   
       
    def testAcronymParsing(self):
        ''' test acronym parsing '''
        title=Title("(ATAED 2020)",ProceedingsTitleParser.acronymGroup)
        title.pyparse()
        md=title.metadata()
        self.assertTrue("acronym" in md)
        self.assertEqual("ATAED 2020",md["acronym"])
          
    def testExampleResult(self):
        ''' test result of examples ''' 
        titlelines=[
            'Proceedings of the Thirty-First AAAI Conference on Artificial Intelligence, February 4-9, 2017, San Francisco, California, USA',
            'Selected proceedings of the 2009 Summit on Translational Bioinformatics.',
            'Proceedings of the International Workshop on Algorithms & Theories for the Analysis of Event Data 2020 (ATAED 2020),virtual workshop, June 24, 2020']   
        expected=[
           {'enum': 'Thirty-First', 'description': None, 'delimiter': None, 'daterange': '4 - 9', 'eventType': 'Conference', 'extract': None, 'field': None, 'frequency': None, 'location': None, 'lookupAcronym': None, 'month': 'February', 'ordinal': None, 'organization': None, 'prefix': 'AAAI', 'province': 'California', 'publish': None, 'scope': None, 'syntax': None, 'topic': 'Artificial Intelligence', 'year': 2017, 'city': 'San Francisco', 'country': 'USA', 'title': 'Proceedings of the Thirty-First AAAI Conference on Artificial Intelligence, February 4-9, 2017, San_Francisco, California, USA'}
           ,       
           {
                'daterange': None,
                'delimiter': None,
                'description': None,
                'enum': None,
                'eventType': 'Summit',
                'extract': 'Selected',
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
                'title': 'Selected proceedings of the 2009 Summit on Translational '
                        'Bioinformatics.',
                'topic': 'Translational Bioinformatics',
                'year': 2009
            },
            {'enum': None, 'description': None, 'delimiter': None, 'daterange': None, 'eventType': 'Workshop', 'extract': None, 'field': None, 'frequency': None, 'location': 'virtual', 'lookupAcronym': None,'month': None, 'ordinal': None, 'organization': None, 'prefix': None, 'province': None, 'publish': None, 'scope': 'International', 'syntax': None, 'topic': 'Algorithms & Theories for the Analysis of Event Data 2020', 'year': None, 'acronym': 'ATAED 2020', 'title': 'Proceedings of the International Workshop on Algorithms & Theories for the Analysis of Event Data 2020 (ATAED 2020),virtual workshop, June 24, 2020'}
        ]
        parser=self.getParser()
        tc=Counter()
        index=0
        for line in titlelines:
            title=self.tryParse(line, parser, tc)
            metadata=title.metadata()
            print(metadata)
            self.assertEqual(expected[index],metadata)
            index+=1
        self.assertEqual(tc["success"],len(titlelines))
        
    def doTestParser(self,tp,minSuccess,limit=50):
        ''' general test Parsing function ''' 
        parser=self.getParser()
        tc=Counter()
        lineCount=0
        for record in tp.records:
            eventId=None
            if "eventId" in record:
                eventId=record["eventId"]
            lineCount=lineCount+1    
            self.tryParse(record["title"],parser,tc,eventId=eventId,doprint=lineCount<=limit)
        print (tc.most_common())
        success=tc['success']
        failed=tc['fail']
        total=success+failed
        print("%5d/%5d %5.1f%%" % (success,total,success/total*100))   
        self.assertGreater(success, minSuccess)
        return tc
        
    def testPyParse(self):
        '''
        test py parsing approach for four samples
        '''
        tcs={}
        tps=self.getTitleParsers()
        delim=""    
        for tp in tps:
            tcs[tp.name]=self.doTestParser(tp,10)
        for tp in tps:
            print("%s%s" % (delim,tp.name),end='')
            delim="&"   
        print("\\\\")
                  
        for key in ['success','fail','eventType','frequency','enum','acronym','year','month','daterange','country','city']:
            print (key,end='')
            for tp in tps:
                tc=tcs[tp.name]
                total=tc['success']+tc['fail']
                print ("&%d&%5.1f%%" %(tc[key],tc[key]/total*100),end='')
            print ("\\\\")
               
    def testPyParseWikiData(self):
        ''' test pyparsing parser '''
        tp=self.getTitleParser("proceedings-wikidata.txt",16000)
        self.doTestParser(tp,15500)
        
    def testPyParseCEUR_WS(self):
        ''' test pyparsing parser with CEUR-WS dataset '''
        tp=self.getTitleParser("proceedings-ceur-ws.txt",2629,mode='CEUR-WS')
        self.doTestParser(tp,2280)
        
    def testPyParseDBLP(self):
        ''' test pyparsing with DBLP dataset '''
        tp=self.getTitleParser("proceedings-dblp.txt",14207,mode='dblp')
        self.doTestParser(tp,13700)
    
    def testPyParseCrossRef(self):
        ''' test py parsing '''
        tp=self.getTitleParser("proceedings-crossref.txt",10000,mode='line')
        self.doTestParser(tp,10000)
     
    def testSeriesEnumeration(self):
        ''' test getting most often used series enumerations of Proceeding Events '''
        tp=self.getTitleParser("proceedings-wikidata.txt",16000)
        d=ProceedingsTitleParser.getDictionary()
        tc=Counter()
        for record in tp.records:
            title=Title(record["title"],dictionary=d)
            title.parse()
            if title.enum is not None:
                if self.debug:
                    print ("%d: %s" % (title.enum,record))
                    print ("    %s" % title.info)
                tc[title.enum]+=1
        print(tc.most_common(250))     
                    
    def doTestTitleParser(self,tp,em,showHistogramm=False):
        ''' test the title parser '''       
        d=ProceedingsTitleParser.getDictionary()
        tokenStats=TokenStatistics(tp.name,d)
        for record in tp.records:
            title=Title(record["title"],d)
            tokenStats.addTokenCount(len(title.tokens))
            for token in title.tokens:
                dtoken=d.getToken(token)
                if dtoken is None:
                    if token in em.eventsByAcronym:
                        dtoken={}
                        dtoken["type"]="acronym"
                        dtoken["label"]=token
                tokenStats.addToken(token,dtoken);
        
        tokenStats.showTypeTable()
        tokenStats.showMostCommon(250)
         
        if showHistogramm:
            title=tp.name.replace(".txt","")
            tokenStats.showHistogramm(title)
          
        return tokenStats
    
    def doCheckCountries(self,statsMap):
        '''
        analyze tokens for potentially missing country entries
        '''
        cm=CountryManager("wikidata")
        cm.fromCache()
        countryMap={}
        for country in cm.countryList:
            countryMap[country['name']]=country;
            
        foundSum=0
        count=0
        foundCountries={}
        for stats in statsMap.values():
            for unknownToken,freq in stats.tc.most_common(10000):
                if unknownToken in countryMap:
                    country=countryMap[unknownToken]
                    foundCountries[country['name']]=country
                    foundSum+=freq
                    count+=1
                    print ("%20s %2s %3d %10.0f %6.0f" % (country["name"],country["isocode"],freq,country["population"],country["gdpPerCapita"]))
        print ("%d/%d: %d" % (count,len(foundCountries),foundSum))  
        for countryName in sorted(foundCountries.keys()):
            country=foundCountries[countryName]
            print("""%s:
    type: country
    isocode: %s
    population: %10.0f
    gpdPerCapita: %6.0f""" % (countryName,country["isocode"],country["population"],country["gdpPerCapita"]) )
    
    def getTitleParsers(self):
        tps=[
                # low expectation due to problem in API
                self.getTitleParser("proceedings-ceur-ws.txt",2629,mode='CEUR-WS'),
                self.getTitleParser("proceedings-dblp.txt",14207,mode='dblp'),
                self.getTitleParser("proceedings-wikidata.txt",16000),
                self.getTitleParser("proceedings-crossref.txt",45300, mode='line')
        ]
        return tps;
        
    def testTitleParser(self):
        ''' test reading the proceeding titles from the sampledata directory'''
        checkCountries=True
       
        showHistogram=True
        opr=OpenResearch()
        opr.initEventManager()
        em=opr.em
        statsMap={}
        counter=Counter()
        for tp in self.getTitleParsers():
            statsMap[tp.name]=self.doTestTitleParser(tp,em,showHistogram) 
            counter[tp.name]=statsMap[tp.name].recordCount  
        print (counter) 
        print ("total # of proceeding titles parsed: %d" % (sum(counter.values())))   
        if checkCountries:
            self.doCheckCountries(statsMap)
             
            
    def testGraph(self):
        g=nx.Graph()
        g.add_edge('A', 'B', weight=4)
        #nx.write_yaml(g, 'g_test1.yaml')
        #nx.write_graphml_lxml(g,'g_test1.graphml')
        
    def testDictionary(self):
        ''' test the dictionary '''
        d=ProceedingsTitleParser.getDictionary()
        print (d.tokens)
        d.addEnums()
        d.addYears()
        print (d.tokens)
        d.write()
        
    def testError(self):
        ''' test error handling according to https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/4 '''
        lookup=Lookup("testError")
        tp=lookup.tp
        self.assertTrue("Innsbruck" in tp.dictionary.tokens)
        titles=['Tagungsband des 17. Workshops "Software Engineering im Unterricht der Hochschulen" 2020 (SEUH 2020),Innsbruck, Österreich, 26. - 27.02.2020.']
        tp.fromLines(titles, 'line')
        tc,errs,result=tp.parseAll()
        # there should be a failed entry in the counter
        self.assertEqual(1,tc["fail"])
        self.assertEqual(1,len(errs))
        err=errs[0]
        self.assertTrue("Expected" in str(err))
        self.assertEqual(1,len(result))
        title=result[0]
        print (title.metadata())
        self.assertTrue('city' in title.metadata())
        print (title.notfound)
        
    def testNERMode(self):
        ''' test named entity recognition mode '''
        lookup=Lookup("testNerMode")
        tp=lookup.tp
        titles=['ATVA 2020 18th International Symposium on Automated Technology for Verification and Analysis',
        'Proceedings of the 8th International Workshop on Bibliometric-enhanced Information Retrieval (BIR)co-located with the 41st European Conference on Information Retrieval (ECIR 2019)Cologne, Germany, April 14th, 2019.']
        tp.fromLines(titles,'line')  
        tc,errs,result=tp.parseAll()
        print (tc)
        print (errs)
        print (result)
        # make sure we have exactly one result
        self.assertEqual(2,len(result))
        for title in result:
            print (title)
            print (title.info)
            print (title.metadata())
            print (title.notfound)
            # make sure we found the relevant event
            self.assertTrue(len(title.events)>0)
            print (title.events)
            for event in title.events:
                print (event.url)
                
    def testExtractMode(self):
        ''' test extract mode '''
        lookup=Lookup("testExtractMode")
        urls=['http://ceur-ws.org/Vol-2635/',
              'http://ceur-ws.org/Vol-2599/',
              'http://ceur-ws.org/Vol-2553/',
              'http://ceur-ws.org/Vol-2512/',
              'http://ceur-ws.org/Vol-2489/',
              'http://ceur-ws.org/',
              'http://ceur-ws.org/Vol-9999/']
        tp=lookup.tp
        tp.fromLines(urls,'line')  
        tc,errs,result=tp.parseAll()
        print (tc)
        print (errs)
        print (result)
        # expect 4 ok 1 fail and 2 invalid/ignored
        self.assertEqual(4,tc['success']);
        self.assertEqual(1,tc['fail']);
    
    # wait for version 3    
    #def testRailroadDiagrams(self):
            
                    
       
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()