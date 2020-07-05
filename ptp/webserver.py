'''
Created on 2020-04-07

@author: wf
'''
from flask import Flask
from flask import render_template
from flask import request
import os
from flask.helpers import send_from_directory
import argparse
import sys
from ptp.titleparser import ProceedingsTitleParser, Title
from ptp.openresearch import OpenResearch
from ptp.event import EventManager
from collections import Counter

scriptdir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='',static_folder=scriptdir+'/../web', template_folder=scriptdir+'/../templates')
ptp=ProceedingsTitleParser.getInstance()
# get the open research EventManager
em=OpenResearch.getEventManager()
  

@app.route('/')
def home():
    return index()
    
def index(titles="",tc=None,errs=None,result=None,message=None):    
    """ render index page with the given parameters"""
    return render_template('index.html',titles=titles,tc=tc,errs=errs,result=result,message=message)

@app.route('/parse', methods=['POST'])
def parseTitles():
    """ endpoint for proceedings title parsing"""
    titles=request.form.get('titles')
    errs=[]
    result=[]
    tc=Counter()
    for line in titles.splitlines():
        title=Title(line,ptp.grammar)
        try: 
            title.pyparse()
            title.lookup(em)
            result.append(title)    
            tc["success"]+=1
        except Exception as ex:
            tc["fail"]+=1
            errs.append(ex)        
    return index(titles,tc,errs,result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Proceedings Title Parser webservice")
    parser.add_argument('--debug',
                                 action='store_true',
                                 help="run in debug mode")
    parser.add_argument('--port',
                                 type=int,
                                 default=5004,
                                 help="the port to use")
    parser.add_argument('--host',
                                 default="0.0.0.0",
                                 help="the host to serve for")
    args=parser.parse_args(sys.argv[1:])
    app.run(debug=args.debug,port=args.port,host=args.host)   
