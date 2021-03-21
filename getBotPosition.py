import math
import picamera
import os
import requests
from time import sleep


def snapshot():
    camera = picamera.PiCamera()    # Setting up the camera
    camera.capture('/home/pi/Documents/pipeline/bot.jpg') # Capturing the image
    print('Picture taken and saved!')

ip = "192.168.0.100"

url = "http://" + ip + ":5000/upload"
print(url)
def send_file():
    local_file_to_send = 'bot.jpg'
    files = {
     'file': (os.path.basename(local_file_to_send), open(local_file_to_send, 'rb'), 'application/octet-stream')
    }
    r = requests.post(url, files=files)

url2 = "http://" + ip + ":5000/match"
def get_match():
    payload = {'imgName': 'bot.jpg'}
    r = requests.get(url2, params=payload)
    return r.text

url3 = "http://" + ip + ":5000/getUserChoice"
def get_user_choice():
    r = requests.get(url3)
    return r.text
