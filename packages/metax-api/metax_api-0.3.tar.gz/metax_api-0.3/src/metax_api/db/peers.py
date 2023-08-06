from .metax_base import Base
from ..request import Response, Request
from ..types import GET

class Peers(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def peers(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/get_online_peers?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def reconnect_to_peers(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/reconnect_to_peers?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response
