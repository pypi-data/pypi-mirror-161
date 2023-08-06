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
  try:
    user_json_url = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    return user_json["displayName"]
  except KeyError:
    return 'Invalid username'
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
  try:
    user_json_url = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    if user_json["description"] == "":
      return 'No description found.'
    else:
      return user_json["description"]
  except KeyError:
    return 'Invalid Username'
def get_friend_count_by_user(username):
  try:
    user_json_url = f"https://friends.roblox.com/v1/users/{get_id_by_username(username)}/friends/count"
    user_json_content = requests.get(user_json_url).text
    user_json = json.loads(user_json_content)
    return user_json["count"]
  except KeyError:
    return "Invalid Username."
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
  try:
    API_URL = f"https://friends.roblox.com/v1/users/{get_id_by_username(username)}/followings?sortOrder=Asc&limit=10"
    user_json = requests.get(API_URL).text
    if '"data": []' in user_json:
      return False
    elif f'"name": "{followUser}"' in user_json:
        return True
  except KeyError:
    return 'Invalid Username'
def isFollow_by_id(userID, followID):
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
def get_universe_id(gameID):
  API_URL = f"https://api.roblox.com/universes/get-universe-containing-place?placeid={gameID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid PlaceID'
  else:
    return API_JSON['UniverseId']
def get_place_id_by_universe_id(universeID):
  """
  This function will convert the PlaceID to the UniverseID. 
  """
  API_URL = f"https://games.roblox.com/v1/games?universeIds={universeID}"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  return ['data'][0]['id']
def get_follower_count_by_user(username):
  try:
    API_URL = f"https://friends.roblox.com/v1/users/{get_id_by_username(username)}/followers/count"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    if API_JSON["count"] == 0:
      return 'The user inputed has not followed anyone.'
    else:
      return API_JSON["count"]
  except KeyError:
    return 'Invalid Username'
def get_follower_count_by_id(id):
  API_URL = f"https://friends.roblox.com/v1/users/{id}/followers/count"
  API_CONTENT = requests.get(API_URL).text
  API_JSON = json.loads(API_CONTENT)
  if "error" in API_JSON:
    return 'Invalid UserID'
  elif API_JSON["count"] == 0:
    return 'The userID inputed has not followed anyone.'
  else:
    return API_JSON["count"]
def can_view_inventory_by_user(username):
  try:
    API_URL = f"https://inventory.roblox.com/v1/users/{get_id_by_username(username)}/can-view-inventory"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    if API_JSON["canView"] == True:
      return True
    else:
      return False
  except KeyError:
    return 'Invalid Username'
def can_view_inventory_by_id(id):
    API_URL = f"https://inventory.roblox.com/v1/users/{id}/can-view-inventory"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    if "error" in API_CONTENT:
      return 'Invalid UserID'
    elif API_JSON["canView"] == True:
      return True
    else:
      return False
def is_owned_by_user(username, itemType, assetID):
  """
  The itemType can be an asset, gamepass, bundle and a badge.
  This function will return True or False.
  """
  USERNAME_URL_CHECK = f"https://users.roblox.com/v1/users/{get_id_by_username(username)}"
  USERNAME_CONTENT = requests.get(USERNAME_URL_CHECK).text
  if "error" in USERNAME_CONTENT:
    return 'Invalid Username'
  elif itemType == "Asset" or itemType == "asset":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Asset/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid AssetID'
  elif itemType == "Badge" or itemType == "badge":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Badge/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid BadgeID'
  elif itemType == "gamepass" or itemType == "Gamepass":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/GamePass/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid GamePassID'
  elif itemType == "bundle" or itemType == "Bundle":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Bundle/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid BundleID'
  else:
    return 'Invalid ItemType'
def is_owned_by_id(id, itemType, assetID):
  """
  The itemType can be an asset, gamepass, bundle and a badge.
  This function will return True or False.
  """
  USERID_URL_CHECK = f"https://users.roblox.com/v1/users/{id}"
  USERID_CONTENT = requests.get(USERID_URL_CHECK).text
  if "error" in USERID_CONTENT:
    return 'Invalid UserID'
  elif itemType == "Asset" or itemType == "asset":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Asset/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid AssetID'
  elif itemType == "Badge" or itemType == "badge":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Badge/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid BadgeID'
  elif itemType == "gamepass" or itemType == "Gamepass":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/GamePass/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid GamePassID'
  elif itemType == "bundle" or itemType == "Bundle":
    try:
      API_URL = f"https://inventory.roblox.com/v1/users/{id}/items/Bundle/{assetID}/is-owned"
      API_CONTENT = requests.get(API_URL).text
      if "false" in API_CONTENT:
        return False
      else:
        return True
    except KeyError:
      return 'Invalid BundleID'
  else:
    return 'Invalid ItemType'
def get_game_description_by_id(gameID):
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]["description"]
  except KeyError:
    return 'Invalid GameID'
def get_game_name_by_id(gameID):
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]["name"]
  except KeyError:
    return 'Invalid GameID'
def get_owner_of_game_by_id(gameID):
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]['creator']["name"]
  except KeyError:
    return 'Invalid GameID'
def get_playing_count_by_id(gameID):
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]["playing"]
  except KeyError:
    return 'Invalid UniverseID'
def get_visits_by_id(gameID):
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]['visits']
  except KeyError:
    return 'Invalid GameID'
def get_placeid_by_universeid(universeID):
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={universeID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON["data"][0]["rootPlaceId"]
  except KeyError:
    return 'Invalid UniverseID'
def isfollowed_by_followUser(username, followedUser):
  try:
    API_URL = f"https://friends.roblox.com/v1/users/{get_id_by_username(username)}/followers?sortOrder=Asc&limit=10"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    for i, stuff in enumerate(API_JSON['data']):
      if i == None:
        continue
      else:
        if API_JSON['data'][i]['name'] == followedUser:
          return True
        elif API_JSON["data"][i]["isBanned"] == True:
          return 'Banned User'
        else:
          return False
  except KeyError:
    return 'Invalid Username'
def isfollowed_by_followID(userID, followedID):
  try:
    API_URL = f"https://friends.roblox.com/v1/users/{userID}/followers?sortOrder=Asc&limit=10"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    for i, stuff in enumerate(API_JSON['data']):
      if i == None:
        continue
      else:
        if API_JSON['data'][i]['name'] == followedID:
          return True
        elif API_JSON["data"][i]["isBanned"] == True:
          return 'Banned User'
        else:
          return False
  except KeyError:
    return 'Invalid UserID'
def get_game_owner_type_by_id(gameID):
  """
  This function will get the owner of the game's type, it can be a Group or a User.
  """
  try:
    API_URL = f"https://games.roblox.com/v1/games?universeIds={get_universe_id(gameID)}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['data'][0]['creator']['type']
  except KeyError:
    return 'Invalid PlaceID'
def get_group_description_by_id(groupID):
  try:
    API_URL = f"https://groups.roblox.com/v1/groups/{groupID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['description']
  except KeyError:
    return 'Invalid GroupID'
def get_group_name_by_id(groupID):
  try:
    API_URL = f"https://groups.roblox.com/v1/groups/{groupID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['name']
  except KeyError:
    return 'Invalid GroupID'
def get_group_owner_by_id(groupID):
  try:
    API_URL = f"https://groups.roblox.com/v1/groups/{groupID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['owner']['name']
  except KeyError:
    return 'Invalid GroupID'
def get_group_owner_display_by_id(groupID):
  try:
    API_URL = f"https://groups.roblox.com/v1/groups/{groupID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['owner']['displayName']
  except KeyError:
    return 'Invalid GroupID'
def get_group_owner_username_by_id(groupID):
  try:
    API_URL = f"https://groups.roblox.com/v1/groups/{groupID}"
    API_CONTENT = requests.get(API_URL).text
    API_JSON = json.loads(API_CONTENT)
    return API_JSON['owner']['username']
  except KeyError:
    return 'Invalid GroupID'
