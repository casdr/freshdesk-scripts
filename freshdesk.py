#!/usr/bin/env python3
import requests
import os
import json
import sys
from requests.auth import HTTPBasicAuth
import urllib.parse

ath = HTTPBasicAuth('api_key', 'x') # fill in your api key
user_id = 34823489 # fill in the nagios contact 
group_id = 2343904 # fill in the group id
subdomain = 'beeh' # fill in the freshdesk subdomain

nagios_name  = sys.argv[1]
problem_type = sys.argv[2]

def qry(org):
	return urllib.parse.quote_plus(org)

def do_request(rtype, url, data={}):
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

def check_match(problem_tag):
	query = qry("cf_nagios_tag: '{0}' AND (status:2 OR status:3 OR status:6 OR status:7)".format(problem_tag))
	r = do_request('GET', 'search/tickets?query="{0}"'.format(query))
	if r['total'] == 0:
		return None
	return r['results'][0]['id']

def add_reply(ticket_id, msg):
	reply = {
		"body": msg,
		"user_id": user_id
	}
	return do_request('POST', 'tickets/{0}/reply'.format(ticket_id), reply)

def set_subject(ticket_id, subject):
	update = {
		"subject": subject
	}
	return do_request('PUT', 'tickets/{0}'.format(ticket_id), data=update)

def create_ticket(problem_tag, subject, msg):
	data = {
		"requester_id": user_id,
		"subject": subject,
		"description": msg,
		"tags": ["nagios_{0}".format(nagios_name)],
		"group_id": group_id,
		"custom_fields": { "cf_nagios_tag": problem_tag }
	}
	return do_request('POST', 'tickets', data)

notification_type = os.environ.get('NAGIOS_NOTIFICATIONTYPE', '')
host_alias = os.environ.get('NAGIOS_HOSTALIAS', '')
host_address = os.environ.get('NAGIOS_HOSTADDRESS', '')
host_state = os.environ.get('NAGIOS_HOSTSTATE', '')
host_output = os.environ.get('NAGIOS_HOSTOUTPUT', '')
service_description = os.environ.get('NAGIOS_SERVICEDESC', '')
service_state = os.environ.get('NAGIOS_SERVICESTATE', '')
long_date = os.environ.get('NAGIOS_LONGDATE', '')
service_output = os.environ.get('NAGIOS_SERVICEOUTPUT', '')

if problem_type == 'service':
	problem_tag = 'service__{0}__{1}'.format(host_alias, service_description)
	subject = "** {0} Service Alert: {1}/{2} is {3} **".format(notification_type, host_alias, service_description, service_state)
	msg = """
***** Nagios *****<br />
<br />
Notification Type: {0}<br />
<br />
Service: {1}<br />
Host: {2}<br />
Address: {3}<br />
State: {4}<br />
<br />
Date/Time: {5}<br />
<br />
Additional Info:<br />
<br />
{6}
""".format(notification_type, service_description, host_alias, host_address, service_state, long_date, service_output)

elif problem_type == 'host':
	problem_tag = 'host__{0}'.format(host_alias)
	subject = "** {0} Host Alert: {1} is {2} **".format(notification_type, host_alias, host_state)
	msg = """
***** Nagios *****<br />
<br />
Notification Type: {0}<br />
Host: {1}<br />
State: {2}<br />
Address: {3}<br />
Info: {4}<br />
<br />
Date/Time: {5}
""".format(notification_type, host_alias, host_state, host_address, host_output, long_date)

else:
	sys.exit(0)


problem_tag = problem_tag.replace(' ', '_')
ticket_id = check_match(problem_tag)
if ticket_id:
	set_subject(ticket_id, subject)
	add_reply(ticket_id, msg)
else:
	create_ticket(problem_tag, subject, msg)
