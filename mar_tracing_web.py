#!/usr/bin/env python3
# #Written by mohlcyber v.0.1 18/09/2019

import sys
import json
import zlib
import base64
import requests

from http.server import BaseHTTPRequestHandler, HTTPServer
from elasticsearch import Elasticsearch

requests.packages.urllib3.disable_warnings()

ELASTIC_IP = 'http://localhost:9200'

EPO_URL = 'https://0.0.0.0'
EPO_PORT = '8443'
EPO_USERNAME = 'username'
EPO_PASSWORD = 'password'


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
            dec_msg = zlib.decompress(base64.b64decode(msg['payload']))
            dec_body = json.loads(dec_msg)

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