import requests
import os
url = "http://10.3.42.46:5000/upload"
def send_file():
    local_file_to_send = 'bot.jpg'
    files = {
     'file': (os.path.basename(local_file_to_send), open(local_file_to_send, 'rb'), 'application/octet-stream')
    }
    r = requests.post(url, files=files)

url2 = "http://10.3.42.46:5000/match"
def get_match():
    payload = {'imgName': 'bot.png'}
    r = requests.get(url2, params=payload)
    print(r.text)

#send_file()
get_match()


