import requests

from luawl.definition import luawl_whitelist
# END OF IMPORTS
luawl_token = ''
luawl_api_url = 'https://api.luawl.com/'

class luawl_object:
	def __init__(self):
		self.token = luawl_token

def send_luawl_request(href, body):
	return requests.post(luawl_api_url + href + '.php', json = body.__dict__).json()

def add_whitelist(discord_id, trial_hours = None, wl_script_id = None):
	body = luawl_object()
	body.discord_id = discord_id
	body.trial_hours = trial_hours
	body.wl_script_id = wl_script_id
	
	return send_luawl_request('whitelistUser', body)

def get_whitelist(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	response = send_luawl_request('getKey', body)
	
	return luawl_whitelist(response)

def delete_whitelist(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	return send_luawl_request('deleteKey', body)

def reset_hwid(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	response = send_luawl_request('resetHWID', body)

	if (type(response) == str):
		return response

	raise Exception(response.get('error'))

def is_on_cooldown(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	return send_luawl_request('isOnCooldown', body)

def remove_cooldown(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	return send_luawl_request('removeCooldown', body)

def update_key_status(discord_id_or_key, key_status: str):
	if (not (key_status == 'Active' or key_status == 'Disabled' or key_status == 'Unassigned' or key_status == 'Assigned')):
		raise Exception('Valid status: Active|Assigned|Disabled|Unassigned')
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key
	body.status = key_status

	return send_luawl_request('updateKeyStatus', body)

def disable_user_key(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	return send_luawl_request('disableKey', body)

def add_blacklist(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	return send_luawl_request('createBlacklist', body)

def remove_blacklist(discord_id_or_key):
	body = luawl_object()
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key

	return send_luawl_request('removeBlacklist', body)

def get_logs(discord_id_or_key_or_hwid):
	body = luawl_object()
	body.discord_id = discord_id_or_key_or_hwid
	body.wl_key = discord_id_or_key_or_hwid
	body.HWID = discord_id_or_key_or_hwid

	return send_luawl_request('getLogs', body)

def get_scripts():
	return send_luawl_request('getAccountScripts', luawl_object())

def get_buyer_role():
	return send_luawl_request('getBuyerRole', luawl_object())

def add_key_tags(discord_id_or_key, tags, wl_script_id):
	body = luawl_object()
	body.wl_script_id = wl_script_id
	body.discord_id = discord_id_or_key
	body.wl_key = discord_id_or_key
	body.tags = tags

	return send_luawl_request('addKeyTags', body)