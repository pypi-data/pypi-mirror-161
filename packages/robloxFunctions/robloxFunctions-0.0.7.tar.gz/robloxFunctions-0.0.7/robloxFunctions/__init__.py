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
  elif f'"name": "{followUser}"' in user_json:
      return True
  else:
    return False
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