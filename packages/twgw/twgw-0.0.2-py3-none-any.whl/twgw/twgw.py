__author__ = "Iyappan"
__email__ = "iyappan@trackerwave.com"
__status__ = "planning"

import requests
from datetime import datetime
import traceback

def get(url, auth):
    """Fetches response using the given url.
    params:
    url: A string of http(s) url to fetch information
    auth: An authentication string
    """
    try:
        s_time = datetime.now().timestamp()
        response = requests.get(url, headers=auth)
        res = {"status": True, "response": response.json(), "time": datetime.now().timestamp() - s_time}
        return res
    except Exception:
        res = {"status": False, "response": None, "exc": str(traceback.format_exc()), "time": datetime.now().timestamp() - s_time}
        return res

def put(url, auth, data):
    """Updates data changes using the given url.
    params:
    url: A string of http(s) url to update information
    auth: An authentication string
    data[optional]: An object/array of data to be updated
    """
    try:
        s_time = datetime.now().timestamp()
        response = requests.put(url, data=data, headers=auth)
        res = {"status": True, "response": response.json(), "time": datetime.now().timestamp() - s_time}
        return res
    except Exception:
        res = {"status": False, "response": None, "exc": str(traceback.format_exc()), "time": datetime.now().timestamp() - s_time}
        return res

def post(url, auth, data):
    """Post data using the given url.
    params:
    url: A string of http(s) url to update information
    auth: An authentication string
    data[optional]: An object/array of data to be posted
    """
    try:
        s_time = datetime.now().timestamp()
        response = requests.post(url, data=data, headers=auth)
        res = {"status": True, "response": response.json(), "time": datetime.now().timestamp() - s_time}
        return res
    except Exception:
        res = {"status": False, "response": None, "exc": str(traceback.format_exc()), "time": datetime.now().timestamp() - s_time}
        return res


# url = "https://liveapi.trackerwave.com/live/api/pf-gateway/gw0011?serverId=5"
# auth = {'content-type': 'application/json', 'API_KEY': 'U7evNMPjsQENFdVEHA38Dh9pajcFlVj2vk60GAtFb0F83R3md0eFRrrtmqr1zkGXDBQpoSEUQdoNIiKLu0OckBEfwQ/+KSWSCTZNvvQ2AIN0cMW5AsvpNPDDGmhXprLi'}
# print(get(url, auth))
