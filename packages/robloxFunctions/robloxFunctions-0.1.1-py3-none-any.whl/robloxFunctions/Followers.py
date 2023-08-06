import json, requests
from .Users import Users
class Followers:
  def isFollow_by_user(username, followUser):
    """
    This function will see if the user has followed the followUser.
    Returns True or False
  """
  try:
    API_URL = f"https://friends.roblox.com/v1/users/{Users.get_id_by_username(username)}/followings?sortOrder=Asc&limit=10"
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
def get_follower_count_by_user(username):
  try:
    API_URL = f"https://friends.roblox.com/v1/users/{Users.get_id_by_username(username)}/followers/count"
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
  def isfollowed_by_followUser(username, followedUser):
    try:
      API_URL = f"https://friends.roblox.com/v1/users/{Users.get_id_by_username(username)}/followers?sortOrder=Asc&limit=10"
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