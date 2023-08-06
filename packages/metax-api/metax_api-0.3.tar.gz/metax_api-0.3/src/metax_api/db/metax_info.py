from .metax_base import Base
from ..request import Response, Request
from ..types import GET
from ..errors import InvalidUUIDError

class MetaxInfo(Base):
	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


	def set_metax_info(self, uuid:str, **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = (
			f"{self.protocol}://{self.host}:{self.port}/config/" +
			f"set_metax_info/?metax_user_uuid={uuid}&{args}"
		)
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def get_metax_info(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']
		
		url = f"{self.protocol}://{self.host}:{self.port}/config/get_metax_info/?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def dump_user_info(self, **query_params:dict) -> Response:

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']
		
		url = f"{self.protocol}://{self.host}:{self.port}/db/dump_user_info/?{args}"
		response = Request(url, GET, **query_params)

		response = response.response()

		self.validate(response)

		return response
		