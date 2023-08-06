import requests
import json
from websocket import create_connection
from .errors import *
from .schemas import *

Q_URL = 'https://ark.fx.co/get-quotes-info'
HLOC_URL = 'https://ark.fx.co/get-quotes-hloc'
SIG_URL = 'https://ark.fx.co/get-signals'
ACCESS_TOKEN = 'eg4q3i2697y9ws42b10p469s'
HEADERS = {
	'Authorization': 'Bearer ' + ACCESS_TOKEN,
	'User-Agent': 'RestSharp/107.3.0.0'
}

class ForexPortalAPI():
	def __init__(self):
		pass

	def getQuoteInfo(self, quote):
		resp = requests.get(
			Q_URL,
			headers = HEADERS,
			params = {
				'_format': 'json',
				'pair': quote
			}
		).json()

		if resp['status'] != 'ok':
			msg = resp['message'] if 'message' in 'resp' \
				else resp['description']
			error = f'Unable to fetch quote "{quote}". Error: {msg}'
			raise UnableToFetchError(error)

		return Quote(**resp['result'][list(resp['result'].keys())[0]])

	def getQuoteHLOC(self, quote, period = 'H1', limit = 400):
		resp = requests.get(
			HLOC_URL,
			headers = HEADERS,
			params = {
				'_format': 'json',
				'pair': quote,
				'limit': limit,
				'period': period
			}
		).json()

		if resp['status'] != 'ok':
			msg = resp['message'] if 'message' in 'resp' \
				else resp['description']
			error = f'Unable to fetch quote "{quote}". Error: {msg}'
			raise UnableToFetchError(error)

		return [
			Tick(
				open = a['Open'],
				high = a['High'],
				low = a['Low'],
				close = a['Close'],
				date = a['Date']
			) for a in resp['result'][list(resp['result'].keys())[0]]['ticks']
		]

	def subscribeQuote(self, quote):
		ws = create_connection('wss://api2-webtrader.ifxdb.com/ws/?EIO=3&token=public&transport=websocket')
		ws.recv()
		ws.recv()
		ws.send('42["tick:subscribe",{"symbols":["' + quote + '"],"type":"standard","digits":4}]')

		while True:
			obj = json.loads(ws.recv()[2:])

			if obj[0] != 'event:quote:tick:standard:4':
				continue

			yield SubTick(**obj[1]['msg'])

	def getQuoteSignals(self, quote, limit = 50):
		resp = requests.get(
			SIG_URL,
			headers = HEADERS,
			params = {
				'from': 0,
				'_format': 'json',
				'pair': quote,
				'limit': limit,
				'trading_system': 3
			}
		).json()
		
		if resp['status'] != 'ok':
			msg = resp['message'] if 'message' in 'resp' \
				else resp['description']
			error = f'Unable to fetch quote "{quote}". Error: {msg}'
			raise UnableToFetchError(error)
		if resp['result'][list(resp['result'].keys())[0]]['pair'] != quote.upper():
			error = f'Unable to fetch quote "{quote}". Error: Invalid quote'
			raise UnableToFetchError(error)

		return [
			Signal(**resp['result'][a]) for a in resp['result']
		]