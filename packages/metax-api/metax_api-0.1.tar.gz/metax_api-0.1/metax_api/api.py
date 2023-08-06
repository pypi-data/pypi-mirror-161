from .db import *
from json import dumps

class Metax(
		Copy,
		Delete,
		Friends,
		Get,
		Keys,
		Listener,
		MetaxInfo,
		Pair,
		Peers,
		Save,
		SendTo,
		Share,
		Update
	):

	def __init__(self, *args:tuple, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)
		socket_args = kwargs['socket'] if 'socket' in kwargs else {}

		self.init_registers(**socket_args)



class CRUD(
		Delete,
		Get,
		Save,
		Update
	):

	def __init__(self, *args:tuple, **kwargs:dict) -> None:
		super().__init__(*args, **kwargs)


