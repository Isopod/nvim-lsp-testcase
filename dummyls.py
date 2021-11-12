#!/bin/env python3

import json
import sys
import re
import string
import getopt


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


def initialize(req):
	send_rpc({
		'jsonrpc': '2.0',
		'id': req.get('id'),
		'result': {
			'capabilities': {
				'textDocumentSync': {
					'openClose': True,
					'change':    1
				}
			}
		}
	});


def nop(req):
	pass

rpc_methods = {
	'initialize':                 initialize,
	'initialized':                nop,
	'shutdown':                   nop,
	'textDocument/didOpen':       nop,
	'textDocument/didChange':     nop,
	'textDocument/didClose':      nop,
	'textDocument/completion':    nop,
	'textDocument/signatureHelp': nop,
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

		# Read body
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
