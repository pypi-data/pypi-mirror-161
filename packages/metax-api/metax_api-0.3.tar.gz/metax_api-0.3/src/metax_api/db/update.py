from .metax_base import Base
from ..request import Response, Request, create_get_params
from ..types import POST, NODE
from ..errors import InvalidUUIDError

class Update(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def update(self, uuid:str, data:str, type:str=NODE, **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		if not isinstance(data, str):
			raise TypeError("Data must be contain string")

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/save/{type}?id={uuid}&{args}"
		response = Request(url, POST, data, **query_params)

		response = response.response()

		self.validate(response)

		return response