'''
Created on 2020-04-07

@author: wf
'''
from flask import Flask, Response
from flask import render_template
from flask import request
import os
from flask.helpers import send_from_directory
import argparse
import sys
from ptp.lookup import Lookup

#from json2xml import json2xml
#https://github.com/vinitkumar/json2xml/issues/59
#from flask_accept import accept

scriptdir=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,static_url_path='',static_folder=scriptdir+'/../web', template_folder=scriptdir+'/../templates')
lookup=Lookup("webserver")

@app.route('/')
def home():
    return index()

def index(titles="",tc=None,errs=None,result=None,message=None,metadebug=True):
    """ render index page with the given parameters"""
    return render_template('index.html',titles=titles,tc=tc,errs=errs,result=result,message=message,metadebug=metadebug,examples=Lookup.getExamples())

@app.route('/parse', methods=['POST','GET'])
#@accept('text/html')
def parseTitles():
    """ endpoint for proceedings title parsing"""
    if request.method == 'POST':
        titleLines=request.form.get('titles')
        metadebug=request.form.get('metadebug')
    else:
        titleLines=request.args.get('titles')
        metadebug=request.args.get('metadebug')    
    metadebug=metadebug is not None    
    tp=lookup.tp
    tp.fromLines(titleLines.splitlines(), 'line',clear=True)
    tc,errs,result=tp.parseAll()
    responseFormat=request.args.get('format')
    if responseFormat is None:
        responseFormat="html"
        # handle content negotiation
        acceptJson=request.accept_mimetypes['application/json'] 
        if acceptJson==1: responseFormat="json"
        acceptXml=request.accept_mimetypes['application/xml']==1 or request.accept_mimetypes['text/xml']==1 
        if acceptXml==1: responseFormat="xml"
    if responseFormat=='json':
        response = Response(status=200,mimetype='application/json')
        jsonText=tp.asJson(result)
        response.set_data(jsonText)
        return response
    elif responseFormat=='xml':
        response = Response(status=200,mimetype='application/xml')
        xml=tp.asXml(result)
        response.set_data(xml)
        return response
    elif responseFormat=='wikison':
        response = Response(status=200,mimetype='text/plain')
        wikison=tp.asWikiSon(result)
        response.set_data(wikison)
        return response
    else:
        return index(titleLines,tc,errs,result,metadebug=metadebug)

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
