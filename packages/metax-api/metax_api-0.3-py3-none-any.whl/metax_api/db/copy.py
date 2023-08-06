from .metax_base import Base
from ..request import Response, Request
from ..types import GET
from ..errors import InvalidUUIDError

class Copy(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def copy(self, uuid:str, **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/copy/?id={uuid}&{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response
