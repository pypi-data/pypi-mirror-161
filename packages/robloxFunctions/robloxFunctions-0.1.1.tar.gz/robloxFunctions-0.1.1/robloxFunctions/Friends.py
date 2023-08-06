from .Users import Users
import json, requests
class Friends:
  """
  I will be adding more features to this.
  """
  def get_friend_count_by_user(username):
    try:
      user_json_url = f"https://friends.roblox.com/v1/users/{Users.get_id_by_username(username)}/friends/count"
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
  