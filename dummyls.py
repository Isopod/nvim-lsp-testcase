#!/bin/env python3

import json
import sys
import re
import string
import getopt

files = {}
identifiers = [
	('Apple',          '(a,b,c)'),
	('ApplePie',       '(x,y)'),
	('Banana',         '(d,e,f)'),
	('BananaSmoothie', '(y,z)'),
	('Cranberry',      '(g,h,i)'),
	('CranberryJuice', '(z,w)'),
	('Date',           '(j,k,l)'),
	('Elderberry',     '(m,n,o)')
]

transcript = open('/dev/null', 'w')
log        = open('/dev/null', 'w')

def shorten(s, max_len=1000):
	if len(s) > max_len:
		return s[0 : max(0, max_len - 3)] + '...'
	else:
		return s

def send_rpc(msg):
	txt = json.dumps(msg)

	print(f'Content-Length: {len(txt)}\r\n\r\n', end='', flush=True)
	print(txt, flush=True)

	print('< ' + shorten(txt), file=log, flush=True)

def get_prefix(s, x):
	result = ''
	if x >= len(s):
		x = len(s) - 1
	if x >= 0 and s[x] == '(':
		x = x - 1
	while x >= 0 and s[x].isalpha():
		result = s[x] + result
		x = x - 1
	return result

def initialize(req):
	send_rpc({
		'jsonrpc': '2.0',
		'id': req.get('id'),
		'result': {
			'capabilities': {
				'textDocumentSync': {
					'openClose': True,
					'change':    1
				},
				'completionProvider': {
					'triggerCharacters':   None,
					'allCommitCharacters': None,
					'resolveProvider':     False
				},
				'signatureHelpProvider': {
					'triggerCharacters': ['(', ','],
					'retriggerCharacters': []
				}
			}
		}
	});

def textdocument_didopen(req):
	uri = req['params']['textDocument']['uri']
	txt = req['params']['textDocument']['text']
	files[uri] = txt.splitlines()

def textdocument_didchange(req):
	uri = req['params']['textDocument']['uri']
	txt = req['params']['contentChanges'][0]['text']
	files[uri] = txt.splitlines()

def textdocument_didclose(req):
	uri = req['params']['textDocument']['uri']
	del files[uri]

def textdocument_completion(req):
	uri = req['params']['textDocument']['uri']
	row = req['params']['position']['line']
	col = req['params']['position']['character']

	prefix = get_prefix(files[uri][row], col)

	send_rpc({
		'jsonrpc': '2.0',
		'id': req.get('id'),
		'result': {
			'isIncomplete': False,
			'items': [
				{
					'label': x[0]
				}
				for x in identifiers
				if x[0].lower().startswith(prefix.lower())
			]
		}
	});

def textdocument_signaturehelp(req):
	uri = req['params']['textDocument']['uri']
	row = req['params']['position']['line']
	col = req['params']['position']['character']

	prefix = get_prefix(files[uri][row], col)

	send_rpc({
		'jsonrpc': '2.0',
		'id': req.get('id'),
		'result': {
			'isIncomplete': False,
			'items': [
				{
					'label': x[0] + x[1]
				}
				for x in identifiers
				if x[0].lower() == prefix.lower()
			]
		}
	});

def nop(req):
	pass

rpc_methods = {
	'initialize':                 initialize,
	'initialized':                nop,
	'shutdown':                   nop,
	'textDocument/didOpen':       textdocument_didopen,
	'textDocument/didChange':     textdocument_didchange,
	'textDocument/didClose':      textdocument_didclose,
	'textDocument/completion':    textdocument_completion,
	'textDocument/signatureHelp': textdocument_signaturehelp,
	'$/cancelRequest':            nop
}


opts, args = getopt.getopt(sys.argv[1:], "", ["save-transcript=", "save-log="])
for o, a in opts:
	if o == '--save-transcript':
		transcript = open(a, 'w')
	elif o == '--save-log':
		log = open(a, 'w')

try:
	while True:
		# Read headers
		content_length = 0
		while True:
			s = sys.stdin.readline().rstrip()
			print(s, end='\r\n', file=transcript, flush=True)
			if s == '':
				break
			m = re.match(r'Content-Length:\s*([0-9]+)', s, re.IGNORECASE)
			if m:
				content_length = int(m.group(1))

		if content_length <= 0:
			break

		body = sys.stdin.read(content_length)

		print(body, end='', file=transcript, flush=True)
		print('> ' + shorten(body), file=log, flush=True)

		req = json.loads(body)

		method = req.get('method')
		_id = req.get('id')

		if method in rpc_methods:
			rpc_methods[method](req)
		else:
			send_rpc({
				'jsonrpc': '2.0',
				'id': _id,
				'error': {
					'code': -32601,
					'message': f'Unknown method: {method}'
				}
			})
except BaseException as error:
	print('An exception occurred: {}'.format(error), file=transcript, flush=True)
	raise
finally:
	transcript.close()
