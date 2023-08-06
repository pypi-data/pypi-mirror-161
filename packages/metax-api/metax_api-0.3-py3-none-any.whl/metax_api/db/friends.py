from .metax_base import Base
from ..request import Response, Request
from ..types import POST
from ..errors import ShareArgumentsError

class Friends(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def add_friend(self, key:str, username:str, **query_params:dict) -> Response:
		data = {
			'key':key,
			'username':username
		}

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/add_friend/?{args}"
		response = Request(url, POST, data,  **query_params)

		response = response.response()

		self.validate(response)

		return response

	def get_friends_list(self, **query_params:dict) -> Response:
		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/config/get_friend_list?{args}"
		response = Request(url, POST, data,  **query_params)

		response = response.response()

		self.validate(response)

		return response
