from requests import get
import json
from stopwatch import Stopwatch

page = 1
stopwatch = Stopwatch()

def repair_mode():
    status = get("https://api.meower.org/status").text
    try:
        load = json.loads(status)
        return load["isRepairMode"]
    except json.decoder.JSONDecodeError:
        pass

def scratch_deprecated():
    status = get("https://api.meower.org/status").text
    try:
        load = json.loads(status)
        return load["scratchDeprecated"]
    except json.decoder.JSONDecodeError:
        pass

def find_post(id):
    global page
    home = get(f"https://api.meower.org/home?page={page}").text
    try:
        load = json.loads(home)
        return load["index"][id]
    except json.decoder.JSONDecodeError:
        pass

def get_home():
    global page
    home = get(f"https://api.meower.org/home?page={page}").text
    try:
        load = json.loads(home)
        return load["index"]
    except json.decoder.JSONDecodeError:
        pass

def home_len():
    global page
    home = get(f"https://api.meower.org/home?page={page}").text
    try:
        load = json.loads(home)
        return len(load["index"])
    except json.decoder.JSONDecodeError:
        pass

def get_post(id):
    post = get(f"https://api.meower.org/posts?id={id}").text
    try:
        load = json.loads(post)
        return f'{load["u"]}: {load["p"]}'
    except json.decoder.JSONDecodeError:
        pass

def page_len():
    global page
    home = get(f"https://api.meower.org/home?page={page}").text
    try:
        load = json.loads(home)
        return load["pages"]
    except json.decoder.JSONDecodeError:
        pass

def current_page():
    global page
    home = get(f"https://api.meower.org/home?page={page}").text
    try:
        load = json.loads(home)
        if (page != load["page#"]):
            page = load["page#"]
        return load["page#"]
    except json.decoder.JSONDecodeError:
        pass

def change_page(page_num):
    global page
    page = page_num

def ping():
    stopwatch.start()
    get("https://api.meower.org/").text
    stopwatch.stop()
    return stopwatch.elapsed

def argo_tunnel():
    res = get("https://api.meower.org/")
    if res.status_code != 200:
        return True
    else:
        return False
   
def stats_chats():
    stats = get("https://api.meower.org/statistics").text
    try:
        load = json.loads(stats)
        return loads["chats"]
    except json.decoder.JSONDecodeError:
        pass
        
def stats_users():
    stats = get("https://api.meower.org/statistics").text
    try:
        load = json.loads(stats)
        return loads["users"]
    except json.decoder.JSONDecodeError:
        pass
        
def stats_posts():
    stats = get("https://api.meower.org/statistics").text
    try:
        load = json.loads(stats)
        return loads["posts"]
    except json.decoder.JSONDecodeError:
        pass

def user_lvl(user):
    user = get(f"https://api.meower.org/users/{user}").text
    try:
        load = json.loads(user)
        return load["lvl"]
    except json.decoder.JSONDecodeError:
        pass

def user_banned(user):
    user = get(f"https://api.meower.org/users/{user}").text
    try:
        load = json.loads(user)
        return load["banned"]
    except json.decoder.JSONDecodeError:
        pass

def user_uuid(user):
    user = get(f"https://api.meower.org/users/{user}").text
    try:
        load = json.loads(user)
        return load["uuid"]
    except json.decoder.JSONDecodeError:
        pass

def user_pfp(user):
    user = get(f"https://api.meower.org/users/{user}").text
    try:
        load = json.loads(user)
        return load["pfp"]
    except json.decoder.JSONDecodeError:
        pass
