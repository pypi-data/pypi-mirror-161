from .metax_base import Base
from ..request import Response, Request
from ..types import GET

class Keys(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def get_user_keys(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']		

		url = f"{self.protocol}://{self.host}:{self.port}/config/get_user_keys?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def get_user_public_key(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/get_user_public_key?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response

	def regenerate_user_key(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/regenerate_user_json?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response
