import math
import picamera
import os
import requests
from time import sleep


def snapshot():
    camera = picamera.PiCamera()    # Setting up the camera
    camera.capture('/home/pi/Documents/pipeline/bot.jpg') # Capturing the image
    print('Picture taken and saved!')

ip = "192.168.0.100"    # ip of web server, will need to change everytime the network ips reset

url = "http://" + ip + ":5000/upload"
print(url)
def send_file():
    local_file_to_send = 'bot.jpg'      # default image name that is sent to the web server after a picture is taken on the camera
    files = {
     'file': (os.path.basename(local_file_to_send), open(local_file_to_send, 'rb'), 'application/octet-stream')
    }
    r = requests.post(url, files=files)

url2 = "http://" + ip + ":5000/match"
def get_match():                        # method that gets a result from the web server. Returns the name of the template that the image matched with
    payload = {'imgName': 'bot.jpg'}
    r = requests.get(url2, params=payload)
    return r.text

url3 = "http://" + ip + ":5000/getUserChoice"
def get_user_choice():                  # returns user selection
    r = requests.get(url3)
    return r.text
