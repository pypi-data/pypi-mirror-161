import os as _os
import requests as _requests
from typing import Callable, Optional, Union, cast

_USER_MESSAGE_ENDPOINT: str = f'http://localhost:{_os.getenv("OPTI_SIDECAR_PORT")}/user-message'

_default_callback_url: Optional[str] = None
_default_callback_headers: Optional[dict] = None
_print_add_record_calls: bool = False

class Job:
	'''Job Utils - Utility methods for use when running Andromeda Jobs'''

	class Keys:
		'''Standard message keys for use when adding a record to the Job Ledger
		Any string is acceptable, these exist as recommendations but bare strings can also be used


		'''
		MIPGAP = 'mipgap'
		STAGE = 'stage'
		INFO = 'info'
		WARN = 'warning'
		ERROR = 'error'
		SYSTEM = 'system'

	@property
	def default_callback_url() -> Optional[str]:
		'''Default callback url for the add_record function'''
		return _default_callback_url
	
	@default_callback_url.setter
	def default_callback_url(value: Optional[str]) -> None:
		'''

		:param value: str: New default callback url for the add_record function

		'''
		global _default_callback_url
		_default_callback_url = value

	@property
	def default_callback_headers() -> Optional[dict]:
		'''Default callback headers for the add_record function'''
		return _default_callback_headers
	
	@default_callback_headers.setter
	def default_callback_headers(value: dict) -> None:
		'''

		:param value: dict: New default callback headers for the add_record function

		'''
		global _default_callback_headers
		_default_callback_headers = value

	@property
	def print_add_record_calls() -> bool:
		'''Print all calls to add_record to standard out as well as adding the record to the Job Ledger'''
		return _print_add_record_calls
	
	@print_add_record_calls.setter
	def print_add_record_calls(value: bool) -> None:
		'''

		:param value: bool: Toggle printing all calls to add_record to standard out in addition to adding the record to the Job Ledger

		'''
		global _print_add_record_calls
		_print_add_record_calls = value

	def add_record(key: str, message: str, callback_url: Union[Callable, Optional[str]]=None, callback_headers: Optional[dict]=None) -> None:
		'''Adds a record to the Job ledger

		:param key: str: Alphanumeric value used to categorize messages in the Job Ledger
		:param message: str: Value that should be written to the Job Ledger
		:param callback_url: str:  (Default value = None) If included then a POST request will be made to the callback_url with the following values in a json-encoded body:
			- key: value of 'key' from the parameters
			- message: value of 'message' from the parameters
			- jobKey: the id of the currently-running job
			- timestamp: UTC timestamp when the record was set
		:param callback_headers: dict:  (Default value = None) If included along with a callback_url then these headers will be included in the callback POST request:

		'''
		if callback_url is None:
			callback_url = Job.default_callback_url or ''
		if callback_headers is None or len(callback_headers) is 0:
			callback_headers = cast(dict, Job.default_callback_headers) or {}
		headers = { 'Content-Type': 'application/json' }
		body = {
			'key': key,
			'message': message,
			'callbackUrl': callback_url,
			'callbackHeaders': callback_headers
		}
		try:
			_requests.post(_USER_MESSAGE_ENDPOINT, json=body, headers=headers)
		except:
			# no-op - will happen when used in Atlas and this is expected
			pass

		if Job.print_add_record_calls is True:
			callback_text = '' if not callback_url else f' :: {callback_url}'
			print(f'{key} :: {message}{callback_text}')
