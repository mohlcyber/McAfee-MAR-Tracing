#!/usr/bin/env python3
# #Written by mohlcyber v.0.1 18/09/2019

import sys
import json
import zlib
import base64
import requests
import argparse

from http.server import BaseHTTPRequestHandler, HTTPServer
from elasticsearch import Elasticsearch

requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser()

parser.add_argument("--elasticsearch_url", "--es_url", help="Elasticsearch cluster / instance URL", required = True)
parser.add_argument("--elasticsearch_index", "--es_index", help="Elasticsearch Index name", required = True)
parser.add_argument("--elasticsearch_document", "--es_document", help="Elasticsearch Document name", required = True)
parser.add_argument("--epo_server_url", "--epo_server", help="EPO Server URL", required = True)
parser.add_argument("--epo_server_port", "--epo_port", help="EPO Server Port", required = False)
parser.add_argument("--epo_username", "--epo_user", help="EPO Username", required = True)
parser.add_argument("--epo_password", "--epo_pwd", help="EPO Password", required = True)
parser.add_argument("--web_server_port", "--web_srv_port", help="Web Server Port", required = False)

args = parser.parse_args()

# default arguments: {EPO_PORT = 8443 / WEB_SERVER_PORT = 8080}

args_ok = args.elasticsearch_url and\
args.elasticsearch_index and\
args.elasticsearch_document and\
args.epo_server_url and\
args.epo_username and\
args.epo_password

if args_ok:
        print('Required arguments OK ! Elasticsearch (URL: {} / Index: {}, Document:{}), EPO Server URL: {}, EPO Username: {}'.format(args.elasticsearch_url,args.elasticsearch_index,args.elasticsearch_document, args.epo_server_url, args.epo_username))
else:
        print("Not all required arguments identified! Script will now terminate. Please see arguments requirements below.")
        parser.print_help()
        sys.exit(0)

# set script main variables from passed arguments 

ELASTIC_IP = args.elasticsearch_url
ELASTIC_INDEX = args.elasticsearch_index
ELASTIC_DOCUMENT = args.elasticsearch_document
EPO_URL = args.epo_server_url

EPO_USERNAME = args.epo_username
EPO_PASSWORD = args.epo_password

EPO_PORT = 8443
try:
    if args.epo_server_port: 
        EPO_PORT = int(args.epo_server_port)
        print('EPO Port set to {}'.format(EPO_PORT))
except:
    print('Invalid EPO Port value received, using default {}'.format(EPO_PORT))

WEB_SERVER_PORT = 8080

try:
    if args.web_server_port: 
        WEB_SERVER_PORT = int(args.web_server_port)
        print('Web Server Port set to {}'.format(WEB_SERVER_PORT))
except:
    print('Invalid Web Server Port value received, using default {}'.format(WEB_SERVER_PORT))



# helper EPO class used to query properties for McAfee Agents

class EPO():
    def __init__(self):
        self.url = EPO_URL
        self.port = EPO_PORT
        self.verify = False

        self.user = EPO_USERNAME
        self.password = EPO_PASSWORD

        self.session = requests.Session()

    def request(self, option, **kwargs):
        try:
            kwargs.setdefault('auth', (self.user, self.password))
            kwargs.setdefault('verify', self.verify)
            kwargs.setdefault('params', {})
            kwargs['params'][':output'] = 'json'

            url = '{}:{}/remote/{}'.format(self.url, self.port, option)

            if kwargs.get('data') or kwargs.get('json') or kwargs.get('files'):
                res = self.session.post(url, **kwargs)
            else:
                res = self.session.get(url, **kwargs)

            return res.text
        except Exception as e:
            print('ERROR: Something went wrong in epo.request. Error: {}'.format(str(e)))
            sys.exit()

# main handler class to deal with data submission to ES

class BodyHandler():
    def __init__(self):
        self.es = Elasticsearch([ELASTIC_IP])
        self.epo = EPO()

    def decoder(self, body):
        obj = json.loads(body)
        payload = obj['records']

        for each_payload in payload:
            msg = each_payload['message']
            try:
                dec_msg = zlib.decompress(base64.b64decode(msg['payload']))
                dec_body = json.loads(dec_msg)
            except Exception as error:
                return
            for trace in dec_body['traces']:
                hostinfo = self.epo.request('system.find', data={'searchText': trace['maGuid']})
                hostinfo = json.loads(hostinfo[3:])
                for host in hostinfo:
                    trace['maName'] = host['EPOComputerProperties.ComputerName']
                    trace['maIpName'] = host['EPOComputerProperties.IPHostName']
                    trace['maIp'] = host['EPOComputerProperties.IPAddress']

            res = self.es.index(index=ELASTIC_INDEX, doc_type=ELASTIC_DOCUMENT, body=json.dumps(dec_body))
            if res['result'] == 'created':
                print('SUCCESS: Successfull ingested new Trace Data into Elasticsearch.')
            else:
                pass


class Handler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = post_data.decode('utf-8')
        handler = BodyHandler()
        handler.decoder(body)

        self._set_response()
        self.wfile.write("Received: {}".format(self.path).encode('utf-8'))


def run(port=WEB_SERVER_PORT):
    try:
        server_address = ('', port)    
        httpd = HTTPServer(server_address, Handler)
        print('Starting MAR Trace Listener ({})...'.format(server_address))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print('Stopping MAR Trace Listener...\n')      
    except Exception as e:
        print("Error (", str(e), ") occurred. Program will now exit.")

if __name__ == '__main__':    
    run(port=WEB_SERVER_PORT)
