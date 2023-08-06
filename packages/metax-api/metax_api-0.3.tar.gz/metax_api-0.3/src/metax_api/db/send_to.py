from .metax_base import Base
from ..request import Response, Request
from ..types import POST
from ..errors import ShareArgumentsError

class SendTo(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def send_to(self, key:str, data:str, **query_params:dict) -> Response:
		data = {
			'key':key,
			'data':data
		}

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/sendto/?{args}"
		response = Request(url, POST, data,  **query_params)

		response = response.response()

		self.validate(response)

		return response
