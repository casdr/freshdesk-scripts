#!/usr/bin/env python3

import requests
import sys
from requests.auth import HTTPBasicAuth
import json

ath = HTTPBasicAuth('api_key', 'x') # fill in your freshdesk api key
subdomain = 'beeh' # fill in your freshdesk subdomain

def do_request(rtype, url, data={}, files={}):
        url = 'https://{0}.freshdesk.com/api/v2/{1}'.format(subdomain, url)
        headers = {
                'Content-Type': 'application/json'
        }
        if rtype == 'GET':
                r = requests.get(url, auth=ath, headers=headers)
        elif rtype == 'POST':
                r = requests.post(url, auth=ath, data=json.dumps(data), headers=headers)
        elif rtype == 'PUT':
                r = requests.put(url, auth=ath, data=json.dumps(data), headers=headers)
        else:
                return False
        return r.json()

agents = do_request('GET', 'agents?per_page=100')
for agent in agents:
    name = agent['contact']['name']
    job_title = agent['contact']['job_title']
    sig = '<div dir="ltr">\r\n<p style="">Kind regards,<br>{0}</p>\r\n<p style="">{{{{ticket.portal_name}}}}</p>\r\n</div>'.format(name)
    if job_title:
            sig = '<div dir="ltr">\r\n<p style="">Kind regards,<br>{0}</p>\r\n<p style="">{1}<br>{{{{ticket.portal_name}}}}</p>\r\n</div>'.format(name, job_title)
    print(do_request('PUT', 'agents/{0}'.format(agent['id']), data={"signature": sig}))
