#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python client for the Factorion RESTful API.
"""

from functools import lru_cache
import os
import requests

from .decorators import requires_api_key, get_api_key, log_backend_warnings
from .. import __version__ as client_version


class BaseAPIClient(object):
	"""
	Base Python client for the RESTful Factorion API. 

	All API methods require an API key.

	The API key must be set by running :code:`factorion configure` from the terminal.
	"""
	def __init__(self, category, endpoint, version):
		"""
		"""
		self._category = category
		self._endpoint = endpoint
		self._version = version


	@property
	def category(self):
		return self._category


	@property
	def endpoint(self):
		return self._endpoint


	@property
	def version(self):
		return self._version


	def url(self, path):
		"""
		Turns a relative path into a full API endpoint url.

		Parameters
		----------
		path: str
			The relative path of the API resource.

		Returns
		-------
		u : str
			The full URL of the API resource.
		"""
		path = path.strip('/')
		return 'https://api.factorion.ai/%s/%s/%s/%s' % (self.category, self.endpoint, self.version, path)


	@requires_api_key
	@log_backend_warnings
	def get(self, path, **params):
		"""
		.. important:: This method requires a valid API key.

		Issues a GET request to the API resource identified by the input path.

		Parameters
		----------
		path: str
			The relative path of the API resource.
		params: dict, optional
			The query parameters of the GET request. Any keyword argument is 
			automatically interpreted as a request parameter, its name is used
			as the parameter name, and its value as the parameter value.

		Returns
		-------
		response: requests.Response
			The response of the API. The request HTTP status code can be accessed
			through `response.status_code`. To check if the request was succesful,
			inspect `response.ok`. When the API returned data, they can be accessed
			through `response.json()`. Supported status codes are:

			200: 
				The request was successful and the API returned some data accessible through
				`response.json()`.
			402: 
				The request failed because your account does not have a valid payment method.
				Check `response.json()['reason']` for more information.
			403: 
				The request failed because some parameter are either invalid or missing.
				Check `response.json()['reason']` for more information.
			404:
				The request failed because the API couldn't yet solve the problem of interest.
				You should typically try again another time. Check `response.json()['reason']`
				for more information.
		"""
		url = self.url(path)
		api_key = get_api_key()
		if 'client_version' not in params:
			params['client_version'] = client_version
		response = requests.get(url, params=params, headers={'x-api-key': api_key, \
			'content-type': 'application/json'})

		return response


	@requires_api_key
	@log_backend_warnings
	def post(self, path, **params):
		"""
		.. important:: This method requires a valid API key.

		Issues a POST request to the API resource identified by the input path.

		Parameters
		----------
		path: str
			The relative path of the API resource.
		params: dict, optional
			The data to be submitted to the API as part of the POST request, as 
			a JSON. Any keyword argument is automatically interpreted as a 
			key of the JSON data that will be submitted to the API, 
			and its value the associated value in the JSON.

		Returns
		-------
		response: requests.Response
			The response of the API. The request HTTP status code can be accessed
			through `response.status_code`. To check if the request was succesful,
			inspect `response.ok`. When the API returned data, they can be accessed
			through `response.json()`.

			Supported status codes are:

			200: 
				The request was successful and the API returned some data accessible through
				`response.json()`.
			402: 
				The request failed because your account does not have a valid payment method.
				Check `response.json()['reason']` for more information.
			403: 
				The request failed because some parameter are either invalid or missing.
				Check `response.json()['reason']` for more information.
			404:
				The request failed because the API couldn't yet solve the problem of interest.
				You should typically try again another time. Check `response.json()['reason']`
				for more information.
		"""
		url = self.url(path)
		api_key = get_api_key()
		if 'client_version' not in params:
			params['client_version'] = client_version
		response = requests.post(url, json=params, headers={'x-api-key': api_key, \
			'content-type': 'application/json'})

		return response


	@lru_cache(maxsize=32)
	def route(path=None, method=None, **params):
		"""
		.. important:: This method requires a valid API key.

		Generic method to issue a GET or a POST request to the API resource identified
		by the input path.

		Parameters
		----------
		path: str
			The relative path of the API resource.

		method: str
			The REST method. Should be either `'GET'` or `'POST'`.

		params: dict, optional
			The data to be submitted to the API as a JSON for POST requests, or
			query parameters in the case of GET requests.

		Returns
		-------
		response: requests.Response
			The response of the API. The request HTTP status code can be accessed
			through `response.status_code`. To check if the request was succesful,
			inspect `response.ok`. When the API returned data, they can be accessed
			through `response.json()`.

			Supported status codes are:

			200: 
				The request was successful and the API returned some data accessible through
				`response.json()`.
			402: 
				The request failed because your account does not have a valid payment method.
				Check `response.json()['reason']` for more information.
			403: 
				The request failed because some parameter are either invalid or missing.
				Check `response.json()['reason']` for more information.
			404:
				The request failed because the API couldn't yet solve the problem of interest.
				You should typically try again another time. Check `response.json()['reason']`
				for more information.

		Raises
		------
		ValueError
			If path is None or method is neither 'GET', nor 'POST'.
		"""
		if path is None or method is None or \
				method.upper() not in ('GET', 'POST'):
			return None

		if method.upper() == 'GET':
			return self.get(path, **params)

		if method.upper() == 'POST':
			return self.post(path, **params)


