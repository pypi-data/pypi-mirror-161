from ..errors import *
from ..request import Response, Request
from ..types import GET, POST
import re

UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

class Base:
	def __init__(self, host:str, port:int, secure:bool=False) -> None:
		self.host = host
		self.port = port
		self.protocol = 'https' if secure else 'http'

		try:
			Request(
				f"{self.protocol}://{self.host}:{self.port}/db",
				GET,
				verify=False,
				timeout=5
			)
		except Exception as e:
			print(e)
			raise MetaxDisabledError('Metax was disabled, pleace enable it')


	def validate(self, response:Response) -> None:
		json = {}
		try:
			json = response.json()
		except:
			pass

		if not response.success:
			if 'error' in json:
				if "Getting file failed" in json['error']:
					raise GettingFileFiledError(json['error'])
				if "Decryption failed" in json['error']:
					raise DecryptionFailedError(json['error'])
				if "Exception" in json['error']:
					raise MetaxRequestException(json['error'])

				raise ResponseError(
						" ".join(
							[
								json['error'],
								':',
								response.raw.url
							]
						)
					)


	def is_valid_uuid(self, uuid:str) -> bool:
		return UUID_PATTERN.match(uuid) != None