from .metax_base import Base
from ..request import Response, Request
from ..types import POST
from ..errors import ShareArgumentsError

class Share(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def share(self, uuid:str, key:str, **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		if not key or len(key) < 30:
			raise ShareArgumentsError("public keys is not defined")

		data = {
			'key':key 
		}

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/share/?id={uuid}&{args}"
		response = Request(url, POST, data,  **query_params)

		response = response.response()

		self.validate(response)

		return response


	def accept_share(self, uuid:str, key:str, iv:str, **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		data = {
			'key':key,
			'iv':iv
		}

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/accept_share/?id={uuid}?{args}"
		response = Request(url, POST, data,  **query_params)

		response = response.response()

		self.validate(response)

		return response
