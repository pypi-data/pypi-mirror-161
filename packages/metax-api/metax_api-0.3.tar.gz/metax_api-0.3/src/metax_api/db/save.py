from .metax_base import Base
from ..request import Response, Request, create_get_params
from ..types import POST, NODE

class Save(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def save(self, data:str='', type:str=NODE, **query_params:dict) -> Response:

		if not isinstance(data, str):
			raise TypeError("data must me contain string")

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/save/{type}?{args}"
		response = Request(url, POST, data, **query_params)

		response = response.response()

		self.validate(response)

		return response