#!/usr/bin/env python
# -*- coding: utf-8 -*
from functools import wraps
import json
import logging
import os
import requests


def get_api_key():
	"""
	Retrieves the store API key, or None if none was provided.
	"""
	home = os.path.expanduser("~")
	path = os.path.join(home, '.factorion')
	file_name = os.path.join(path, 'config')
	try:
		with open(file_name, 'r') as f:
			config = json.load(f)
			existing_key = config.get('FACTORION_API_KEY', None)
			return existing_key
	except:
		return os.environ.get('FACTORION_API_KEY', None)

	return None


def has_api_key():
	"""
	Returns whether or not an API key was provided as a result of running 
	:code:`factorion configure`.
	"""
	return get_api_key() is not None


def requires_api_key(method):
	"""
	Decorator used to make functions and methods calls fail
	when they require an API key and the user did not provide one 
	by running :code:`factorion configure`. The decorated function or method 
	is otherwise not affected.

	Raises
	------
	AssertionError
		If an API key was not previously recorded.
	"""
	@wraps(method)
	def wrapper(*args, **kw):		
		assert has_api_key(), "An API key should be provided. Please run 'factorion configure'"
		return method(*args, **kw)

	return wrapper


def log_backend_warnings(method):
	"""
	Decorator used to make requests hitting the backend log backend warnings.
	"""
	@wraps(method)
	def wrapper(*args, **kw):
		response = method(*args, **kw)
		try:
			if response.status_code == requests.codes.ok:
				response_json = response.json()
				if 'warning' in response_json:
					logging.warning('%s' % response_json['warning'])
		except:
			pass
		return response

	return wrapper



