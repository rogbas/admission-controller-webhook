#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

import time
import json


from datetime import datetime, timedelta
# from openshift import Model, Missing

osd_group_prefix = "osd-sre-"
osd_sre_admin_group = "osd-sre-admins"


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        body = self._read_body()
        handle_request(event=self, body=body)

    def _read_body(self):
        if 'content-length' in self.headers:
            length = int(self.headers['content-length'])
            return self.rfile.read(length) if length > 0 else None
        return None

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting webhook server...')
    httpd.serve_forever()

def handle_request(event, body):
    # Process request

    body_dict = json.loads(body)

    request = body_dict['request']
    group_name = request['object']['metadata']['name']
    userinfo = request['userInfo']

    print("REQUEST BODY => {}".format(request))
    
    if group_name.startswith(osd_group_prefix):
        print("Performing action: {} in {} group".format(request['operation'], group_name))
        if osd_sre_admin_group in userinfo['groups']:
            response_body = response_allow(request=request)
        else:
            deny_msg = "User not authorized to {} group {}".format(request['operation'], group_name)
            response_body = response_deny(request=request, msg=deny_msg)
    else:
        response_body = response_allow(request=request)

    print("RESPONSE BODY => {}".format(response_body))
    event.wfile.write(response_body)


def response_allow(request):
    return response_base(request=request, allowed=True)


def response_deny(request, msg="Prohibited resource for this cluster"):
    print("Denying admission {}: {}".format(request['uid'], msg))
    print("Request: {}".format(request))
    return response_base(request=request, allowed=False, msg=msg)

def response_base(request, allowed, msg=''):
    body = {
        'apiVersion': 'admission.k8s.io/v1beta1',
        'kind': 'AdmissionReview',
        'response': {
            'uid': request['uid'],
            'allowed': allowed,
            'status': {
                'message': msg
            }
        }
    }
    return json.dumps(body)
    

if __name__ == "__main__":
    from sys import argv

    time_start = time.time()  # start time


    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()