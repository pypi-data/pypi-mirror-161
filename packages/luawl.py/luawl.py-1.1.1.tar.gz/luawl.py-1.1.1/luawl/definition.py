import json

class luawl_whitelist(object):
	def __init__(self, value):
		if (type(value) == dict):
			self.__dict__.update(value)
		else:
			raise Exception(value)

	@property
	def discord_id(self):
		return self.__dict__.get('discord_id')

	@property
	def wl_key(self):
		return self.__dict__.get('wl_key')

	@property
	def HWID(self) -> str:
		return self.__dict__.get('HWID')

	@property
	def key_status(self) -> str:
		return self.__dict__.get('key_status')

	@property
	def is_trial(self) -> bool:
		return self.__dict__.get('isTrial') == 1

	@property
	def expiration(self):
		return self.__dict__.get('expiration')

	@property
	def hours_remaining(self):
		return self.__dict__.get('hours_remaining')

	@property
	def wl_script_id(self):
		return self.__dict__.get('wl_script_id')

	def __str__(self):
		return json.dumps(self.__dict__)