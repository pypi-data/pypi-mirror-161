from .metax_base import Base
from ..request import Response, Request
from ..types import GET
from ..errors import InvalidUUIDError

class Pair(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def start_pairing(self, timeout:int, **query_params:dict) -> Response:
		if not isinstance(timeout, int):
			raise TypeError("timeout must be int")

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/start_pairing/?timeout={timeout}&{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def cancel_pairing(self, **query_params:dict) -> Response:
		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/cancel_pairing/?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def get_pairing_peers(self, **query_params:dict) -> Response:
		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/get_pairing_peers/?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response
		