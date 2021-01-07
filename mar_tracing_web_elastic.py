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
parser.add_argument("--epo_server_url", "--epo_server", help="EPO Server URL", required = True)
parser.add_argument("--epo_server_port", "--epo_port", help="EPO Server URL", required = False)
parser.add_argument("--epo_username", "--epo_user", help="EPO Username", required = True)
parser.add_argument("--epo_password", "--epo_pwd", help="EPO Password", required = True)

args = parser.parse_args()

args_ok = args.elasticsearch_url and args.epo_server_url and args.epo_username and args.epo_password

if args_ok:
	print('Arguments OK ! Elasticsearch URL: {}, EPO Server URL: {}, EPO Username: {}'.format(args.elasticsearch_url, args.epo_server_url, args.epo_username))
else:
	print("No arguments identified! Script will now terminate. Please see arguments requirements below.")
	parser.print_help()
	sys.exit(0)

# set script main variables from passed arguments 
ELASTIC_IP = args.elasticsearch_url
EPO_URL = args.epo_server_url
EPO_PORT = '8443'
if args.epo_server_port: 
	EPO_PORT = args.epo_server_port
	print('EPO Port set to {}'.format(EPO_PORT))
EPO_USERNAME = args.epo_username
EPO_PASSWORD = args.epo_password

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

            res = self.es.index(index='mar', doc_type='trace', body=json.dumps(dec_body))
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


def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, Handler)
    print('Starting MAR Trace Listener...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping MAR Trace Listener...\n')


if __name__ == '__main__':
    run(port=8080)
