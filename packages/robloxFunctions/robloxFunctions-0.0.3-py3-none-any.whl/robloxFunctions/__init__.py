import requests, json
from random import randint
def get_display_by_id(id):
  user_json_url = f"https://users.roblox.com/v1/users/{id}"
  user_json_content = requests.get(str(user_json_url)).text
  user_json = json.loads(user_json_content)
  return user_json["displayName"]
def get_random_display():
  """
  This will get a random valid roblox display name. If the random user doesn't have a display name, it will give the normal username.
  """
  while True:
    user_id = randint(1, 500000000)
    user_json_url = f"https://users.roblox.com/v1/users/{user_id}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if user_json['isBanned'] == False:
      return user_json['displayName']
      break
    else:
      continue
def get_username_by_id(user_id):
  """
  This function will convert your username to a user ID.
  """
  user_json_url = f"https://users.roblox.com/v1/users/{user_id}"
  user_json_content = requests.get(user_json_url).text
  user_json = json.loads(user_json_content)
  return {user_json["name"]}
def get_id_by_username(username):
  """
  This function will convert your user's ID into a username.
  """
  convert_url = f"https://api.roblox.com/users/get-by-username?username={username}"
  convert_content = requests.get(convert_url).text
  convert_json = json.loads(convert_content)
  return convert_json["Id"]
def get_display_by_username(username):
  user_json_url = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
  user_json_content = requests.get(user_json_url).text
  user_json = json.loads(user_json_content)
  return user_json["displayName"]
def get_url_by_username(username):
  user_json_url = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
  user_json_content = requests.get(user_json_url).text
  user_json = json.loads(user_json_content)
  if user_json['isBanned'] == False:
    return f"https://web.roblox.com/users/{user_json['name']}"
def get_url_by_id(id):
  user_json_url = f"https://users.roblox.com/v1/users/{id}"
  user_json_content = requests.get(user_json_url).text
  user_json = json.loads(user_json_content)
  if user_json['isBanned'] == False:
    return f"https://web.roblox.com/users/{user_json['id']}"
def get_random_id():
  """
  This function will give a random valid user ID.
  """
  while True:
    user_id = randint(1, 500000000)
    user_json_url = f"https://users.roblox.com/v1/users/{user_id}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if user_json['isBanned'] == False:
      print(user_json['id'])
      break
    else:
      continue
def get_random_url():
  """
  This will get a random valid roblox user's url.
  """
  while True:
    user_id = randint(1, 500000000)
    user_json_url = f"https://users.roblox.com/v1/users/{user_id}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if user_json['isBanned'] == False:
      return f"https://web.roblox.com/users/{user_json['name']}"
      break
    else:
      continue
def get_random_user():
  """
  This will get a random valid roblox username.
  """
  while True:
    user_id = randint(1, 500000000)
    user_json_url = f"https://users.roblox.com/v1/users/{user_id}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if user_json['isBanned'] == False:
      return f"{user_json['name']}"
      break
    else:
      continue
def get_description_by_id(id):
    user_json_url = f"https://users.roblox.com/v1/users/{id}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if "error" in user_json:
      return 'Invalid ID'
    elif user_json["description"] == "":
      return 'No description found.'
    else:
      return user_json["description"]
def get_description_by_user(username):
    user_json_url = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if "error" in user_json:
      return 'Invalid Username'
    elif user_json["description"] == "":
      return 'No description found.'
    else:
      return user_json["description"]
def get_friend_count_by_user(username):
  user_json_url = f"https://friends.roblox.com/v1/users/{get_id_by_username(username)}/friends/count"
  user_json_content = requests.get(user_json_url).text
  user_json = json.loads(user_json_content)
  if "message" in user_json:
    return "Invalid Username."
  else:
    return user_json["count"]
def get_friend_count_by_id(id):
  user_json_url = f"https://friends.roblox.com/v1/users/{id}/friends/count"
  user_json_content = requests.get(user_json_url).text
  user_json = json.loads(user_json_content)
  if "message" in user_json:
    return "Invalid user ID."
  else:
    return user_json["count"]
def isFollow_by_user(username, followUser):
  """
  This function will see if the user has followed the followUser.
  Returns True or False
  """
  API_URL = f"https://friends.roblox.com/v1/users/{get_id_by_username(username)}/followings?sortOrder=Asc&limit=10"
  user_json = requests.get(API_URL).text
  if '"data": []' in user_json:
    return False
  else:
    if f'"name": "{followUser}"' in user_json:
      return True
def isFollow_by_user(userID, followID):
  """
  This function will see if the user has followed the follow user.
  Returns True or False
  """
  API_URL = f"https://friends.roblox.com/v1/users/{userID}/followings?sortOrder=Asc&limit=10"
  user_json = requests.get(API_URL).text
  if '"data": []' in user_json:
    return False
  elif f'"name": "{followID}"' in user_json:
      return True
  else:
      return False
def get_follower_count_by_user(username):
  API_URL = f"https://friends.roblox.com/v1/users{get_id_by_username(username)}/followers/count"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid Username'
  elif API_JSON["count"] == 0:
    return 'The user inputed has not followed anyone.'
  else:
    return API_JSON["count"]
def get_follower_count_by_id(id):
  API_URL = f"https://friends.roblox.com/v1/users{id}/followers/count"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid UserID'
  elif API_JSON["count"] == 0:
    return 'The userID inputed has not followed anyone.'
  else:
    return API_JSON["count"]
def can_view_inventory_by_user(username):
  API_URL = f"https://inventory.roblox.com/v1/users/{get_id_by_username(username)}/can-view-inventory"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid Username'
  elif API_JSON["canView"] == True:
    return True
  else:
    return False
def can_view_inventory_by_id(id):
  API_URL = f"https://inventory.roblox.com/v1/users/{id}/can-view-inventory"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid UserID'
  elif API_JSON["canView"] == True:
    return True
  else:
    return False
def is_owned_by_user(username, itemType, assetID):
  """
  The itemType can be an asset, gamepass, bundle and a badge. If not it will return an error.
  This function will return True or False.
  """
  USERNAME_URL_CHECK = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
  USERNAME_CONTENT = requests.get(USERNAME_URL_CHECK).text
  if "error" in USERNAME_CONTENT:
    return 'Invalid Username'
  elif itemType == "Asset" or itemType == "asset":
    API_URL = f"https://inventory.roblox.com/v1/users/{get_id_by_username(username)}/items/Asset/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid AssetID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  elif itemType == "Badge" or itemType == "badge":
    API_URL = f"https://inventory.roblox.com/v1/users/{get_id_by_username(username)}/items/Badge/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid BadgeID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  elif itemType == "gamepass" or itemType == "Gamepass":
    API_URL = f"https://inventory.roblox.com/v1/users/{get_id_by_username(username)}/items/GamePass/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid GamePassID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  elif itemType == "bundle" or itemType == "Bundle":
    API_URL = f"https://inventory.roblox.com/v1/users/{get_id_by_username(username)}/items/Bundle/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid BundleID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  else:
    return 'Invalid ItemType'
def is_owned_by_id(id, itemType, assetID):
  """
  The itemType can be an asset, gamepass, bundle and a badge. If not it will return an error.
  This function will return True or False.
  """
  USERID_URL_CHECK = f"https://users.roblox.com/v1/users/{id}"
  USERID_CONTENT = requests.get(USERID_URL_CHECK).text
  if "error" in USERID_CONTENT:
    return 'Invalid UserID'
  elif itemType == "Asset" or itemType == "asset":
    API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Asset/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid AssetID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  elif itemType == "Badge" or itemType == "badge":
    API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Badge/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid BadgeID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  elif itemType == "gamepass" or itemType == "Gamepass":
    API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/GamePass/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid GamePassID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  elif itemType == "bundle" or itemType == "Bundle":
    API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Bundle/{assetID}/is-owned"
    API_CONTENT = requests.get(API_URL).text
    if "error" in API_CONTENT:
      return 'Invalid BundleID'
    elif "false" in API_CONTENT:
      return False
    else:
      return True
  else:
    return 'Invalid ItemType'
"""
def get_gameid_by_name(gameName):
  This function will return the gameID of a game by its name.
  This may not be perfected.
  SEARCH_URL = f"https://web.roblox.com/discover/?Keyword={gameName}"
  SEARCH_CONTENT = requests.get(SEARCH_URL).text
  soup = BeautifulSoup(SEARCH_CONTENT, 'html.parser')
  if '<div data-testid="game-search-no-results" class="font-bold">No Results Found</div>' in SEARCH_CONTENT:
    return 'No Game was found.'
  else:
    for a in soup.find_all('a', class_="game-card-link", href=True):
      if gameName in a.href:
        convert_1 = gameName.split('/')
        convert_2 = gameName.split('?')
        return convert_2[4]
      else:
        continue
"""
def get_game_description_by_id(gameID):
  API_URL = f"https://games.roblox.com/v1/games?universeIds={gameID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid GameID'
  else:
    return API_JSON["description"]
def get_game_name_by_id(gameID):
  API_URL = f"https://games.roblox.com/v1/games?universeIds={gameID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid GameID'
  else:
    return API_JSON["name"]
def get_owner_of_game_by_id(gameID):
  API_URL = f"https://games.roblox.com/v1/games?universeIds={gameID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid GameID'
  else:
    return API_JSON["name"]
def get_playing_count_by_id(gameID):
  API_URL = f"https://games.roblox.com/v1/games?universeIds={gameID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid GameID'
  else:
    return API_JSON["playing"]

def get_badge_name_by_id(badgeID):
  API_URL = f"https://inventory.roblox.com/v1/badges/{badgeID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid BadgeID'
  else:
    return API_JSON["name"]
def get_badge_description_by_id(badgeID):
  API_URL = f"https://inventory.roblox.com/v1/badges/{badgeID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid BadgeID'
  else:
    return API_JSON["description"]