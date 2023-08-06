from requests import *
from .errors import RequestTypeError
from json import loads
from .types import GET, POST

class Response(object):
	def __init__(self, request:any) -> None:
		self.status = request.status_code
		self.data = request.content
		self.as_string = self.data.decode()
		self.success = self.status == 200
		self.raw = request

	def json(self) -> dict:
		return loads(self.as_string)

	def text(self) -> str:
		return self.__str__()

	def __str__(self) -> str:
		return self.as_string



class Request(object):
	data = None
	def __init__(self, url:str, method:int=GET, data:str=None, **params:dict) -> None:
		self.url = url
		self.request(method, data, **params)


	def reload(self, method:int=GET, data:str='', **params:dict) -> any:
		return self.request(method, data, parmas)


	def request(self, method:int, data:str=None, **params:dict):
		if method == 1:
			self.data = self.post(data, **params)
		elif method == 0:
			self.data = self.get(**params)
		else:
			raise RequestTypeError('Unknow Request Method, available (GET, POST)')

		return self.data


	def post(self, data:str, **params:dict) -> post:
		return post(self.url, data, **params)


	def get(self, **params:dict) -> get:
		return get(self.url, **params)


	def __str__(self) -> str:
		return self.data.content.decode()


	def response(self) -> Response:
		return Response(self.data)

def create_get_params(params:dict) -> str:
	s = []
	for key, value in params.items():
		s.append(f"{key}={value}")

	return "&".join(s)
