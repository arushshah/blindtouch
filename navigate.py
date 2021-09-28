from simple_pid import PID
import RPi.GPIO as GPIO
import time
from time import sleep
import math
import getBotPosition

# rotator pins
motorPin1 = 19
motorPin2 = 26

# extruder pins
motorPin3 = 24
motorPin4 = 23

# rotator encoder pins
clkRot = 22
dtRot = 27

# extruder encoder pins
clkExt = 21
dtExt = 20

rotSpeed = 12 # range from 0-100

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(motorPin1, GPIO.OUT)
GPIO.setup(motorPin2, GPIO.OUT)
GPIO.setup(motorPin3, GPIO.OUT)
GPIO.setup(motorPin4, GPIO.OUT)

GPIO.setup(clkRot, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dtRot, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(clkExt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dtExt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# configure pwm for rotator
pwm1 = GPIO.PWM(motorPin1, 100)
pwm2 = GPIO.PWM(motorPin2, 100)

# configure pwm for extruder
pwm3 = GPIO.PWM(motorPin3, 100)
pwm4 = GPIO.PWM(motorPin4, 100)


# code to test rotation motor
'''
rotSpeed = 20
pwm1.start(rotSpeed)
pwm2.start(0)
'''

# rotate the other way
'''
rotSpeed = 20
pwm2.start(rotSpeed)
pwm1.start(0)
'''

# code to test extrusion motor - extrude out
'''
extSpeed = 20
pwm3.start(extSpeed)
pwm4.start(0)
'''
# code to test extrusion motor - extrude in
'''
extSpeed = 20
pwm4.start(extSpeed)
pwm3.start(0)
'''


screenResolution = [2048, 1413]

# code starts here - take picture of the screen once device is placed on the display
getBotPosition.snapshot()
# send the image to the web server
getBotPosition.send_file()
# get the name of the matched template that the web service found
s = getBotPosition.get_match()
arr = s.split(",")
print(arr)
# get the coordinates that the device is placed on relative to the screen
botCoords = [int(arr[1]), screenResolution[1] - int(arr[2])]
#botCoords = [716, 1413-1284]
print(botCoords)


while True:
        user_choice = "Error"
        # do nothing until the user makes a selection in the web interface
        while (user_choice == "Error"):
                user_choice = getBotPosition.get_user_choice()

        user_choice = user_choice.split(",")
        print("User choice: " + str(user_choice))
        sleep(2)
        print(user_choice[0])
        print(user_choice[1])
        print(int(user_choice[0]))
        print(int(user_choice[1]))

        # get the coordinates of the user selection on the touchscreen display
        selectionCoords = [int(user_choice[0]), screenResolution[1] - int(user_choice[1])]

        # calculate the distance and angle from the device coordinates to the user selection coordinates

        distance = math.sqrt((selectionCoords[0] - botCoords[0])**2 + (selectionCoords[1] - botCoords[1])**2)
        # 1st quadrant
        if ((selectionCoords[0] - botCoords[0]) >= 0 and
        (selectionCoords[1] - botCoords[1]) >= 0):
                angle = math.degrees(math.atan((abs(selectionCoords[1] - botCoords[1])*1.0) /(abs(selectionCoords[0] - botCoords[0]))))
        # 2nd quadrant
        elif ((selectionCoords[0] - botCoords[0]) < 0 and
        (selectionCoords[1] - botCoords[1]) >= 0):
                angle = 180-math.degrees(math.atan((abs(selectionCoords[1] - botCoords[1])*1.0) / (abs(selectionCoords[0] - botCoords[0]))))
        # 3rd quadrant
        elif (selectionCoords[0] - botCoords[0] < 0 and selectionCoords[1] - botCoords[1] < 0):
                angle = 180+math.degrees(math.atan((abs(selectionCoords[1] - botCoords[1])*1.0) / (abs(selectionCoords[0] - botCoords[0]))))
        # 4th quadrant
        else:
                angle = 360-math.degrees(math.atan((abs(selectionCoords[1] - botCoords[1])*1.0) / (abs(selectionCoords[0] - botCoords[0]))))

        # rotate as little as possible, never more than 180 degrees
        if (angle > 180):
                angle = -(360-angle)

        print("Angle: " + str(angle))
        print("Distance: " + str(distance))

        # encoder ticks per revolution
        ticksPerRev = 13500
        # how many ticks are needed to reach the desired angle
        ticksNeeded = ticksPerRev * angle / 360

        counter = 0
        clkLastState = GPIO.input(clkRot)

        # loop to rotate device to desired angle
        if (angle > 0):
                pwm1.start(rotSpeed)
                pwm2.start(0)
        elif (angle < 0):
                pwm2.start(rotSpeed)
                pwm1.start(0)

        try:
                while True:
                        clkState = GPIO.input(clkRot)
                        if clkState != clkLastState:
                                dtState = GPIO.input(dtRot)
                                if dtState != clkState:
                                        counter += 1
                                else:
                                        counter -= 1
                        clkLastState = clkState
                        if (abs(counter) > abs(ticksNeeded)):
                                pwm1.start(0)
                                pwm2.start(0)
                                break

        except:
                print("Rotation error")

        counter = 0
        clkLastState = GPIO.input(clkExt)

        # loop to extrude tape to desired distance
        pwm3.start(50)
        pwm4.start(0)

        ticksPerCm = 150
        pixelsPerCm = 130
        ticksNeeded = distance/pixelsPerCm * ticksPerCm
        print("Ticks needed: " + str(ticksNeeded))

        try:
                while True:
                        clkState = GPIO.input(clkExt)
                        if clkState != clkLastState:
                                dtState = GPIO.input(dtExt)
                                if dtState != clkState:
                                        counter += 1
                                else:
                                        counter -= 1
                        clkLastState = clkState
                        if (abs(counter) > abs(ticksNeeded)):
                                pwm3.start(0)
                                pwm4.start(0)
                                break

        except:
                print("Extrusion error")

        sleep(2)

        # loop to retract the tape back into the device
        counter = 0
        ticksNeeded = distance/pixelsPerCm * ticksPerCm
        pwm4.start(50)
        pwm3.start(0)
        try:
                while True:
                        clkState = GPIO.input(clkExt)
                        if clkState != clkLastState:
                                dtState = GPIO.input(dtExt)
                                if dtState != clkState:
                                        counter += 1
                                else:
                                        counter -= 1
                        clkLastState = clkState
                        if (abs(counter) > abs(ticksNeeded)):
                                pwm3.start(0)
                                pwm4.start(0)
                                break

        except:
                print("Extrusion 2 error")


        # loop to reset angle of the device to home position
        counter = 0
        ticksNeeded = ticksPerRev * angle / 360

        if (angle > 0):
                pwm2.start(rotSpeed)
                pwm1.start(0)
        elif (angle < 0):
                pwm1.start(rotSpeed)
                pwm2.start(0)

        try:
                while True:
                        clkState = GPIO.input(clkRot)
                        if clkState != clkLastState:
                                dtState = GPIO.input(dtRot)
                                if dtState != clkState:
                                        counter += 1
                                else:
                                        counter -= 1
                        clkLastState = clkState
                        if (abs(counter) > abs(ticksNeeded)):
                                pwm1.start(0)
                                pwm2.start(0)
                                break

        except:
                print("Rotation error")