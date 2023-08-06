from .metax_base import Base
from ..request import Response, Request
from ..types import POST, ANY, UPDATE, DELETE
from ..errors import InvalidUUIDError, UnknownUUIDError
from websocket import WebSocketApp
from threading import Thread
from json import loads

class Event:
	def __init__(self, type:str, uuid:str, full_event:dict) -> None:
		self.target = uuid
		self.type = type
		self.event = full_event


class Listener(Base):
	__listeners = []
	any_event = lambda *a, **k:...


	def __init__(self, *args:list, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)
		self.init_registers()

	def listeners(self) -> list:
		return self.__listeners


	def register_listener(self, uuid:str, callback:callable, type_:str=ANY,  **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		if not callable(callback):
			raise TypeError("CALLBACK is not a function")

		if type_ not in [ANY, DELETE, UPDATE]:
			raise TypeError("invalid callback type")

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/register_listener?id={uuid}&{args}"
		response = Request(url, POST, **query_params)

		response = response.response()

		if response.success:
			self.__listeners.append({
				'callback':callback,
				'uuid':uuid,
				'type':type_
			})

		self.validate(response)

		return response


	def unregister_listener(self, uuid:str, **query_params:dict) -> Response:
		if not self.is_valid_uuid(uuid):
			raise InvalidUUIDError(f"'{uuid}' is not uuid")

		have = any([ uuid == item['uuid'] for item in self.__listeners])
		if not have:
			raise UnknownUUIDError(f'Unknown UUID {uuid}')

		args = ''
		if 'GET' in query_params:
			args = create_get_params(query_params['GET'])
			del query_params['GET']

		url = f"{self.protocol}://{self.host}:{self.port}/db/unregister_listener?id={uuid}&{args}"
		response = Request(url, POST, **query_params)

		response = response.response()

		self.validate(response)

		return response


	def init_registers(self, *args:list, **kwargs:dict) -> None:
		self.socket = WebSocketApp(
			f"ws://{self.host}:{self.port}",
			on_message = self.on_ws_message
		)

		self.ws_thread = Thread(target=self.socket.run_forever,
			args=args, kwargs=kwargs)
		self.ws_thread.start()

		return self.ws_thread


	def event(self, response:str) -> None:
		event = response['event']
		uuid = response['uuid'] if 'uuid' in response else None

		if callable(self.any_event):
			self.any_event(Event(event, uuid, response))

		for listener in self.__listeners:
			if listener['type'] == event and listener['uuid'] == uuid:
				listener['callback'](Event(event, uuid, response))
			elif listener['type'] == ANY and listener['uuid'] == uuid:
				listener['callback'](Event(event, uuid, response))


	def on_ws_message(self, socket:WebSocketApp, message:str) -> None:
		response = loads(message)
		if 'event' in response:
			self.event(response)
