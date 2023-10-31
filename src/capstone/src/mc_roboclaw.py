#!/usr/bin/env python3

import atexit
from roboclaw_3 import Roboclaw
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32
import time

#Gyro needs
import math
#import wx
from sensor_msgs.msg import Imu
from tf.transformations import euler_from_quaternion
import RPi.GPIO as GPIO
rad2degrees = 180.0/math.pi
precision = 2 #round to this number of digits

#using GPIO 14/15 which are the default serial ports
#to enable more you will have to edit cmdline.txt
address = 0x80
roboclaw = Roboclaw("/dev/ttyS0", 115200)
#roboclaw = Roboclaw("/dev/ttyACM0", 115200) #too use usb - roboclaw uncomment this line
roboclaw.Open()

#roboclaw needs atleast one turning  mvcommand and forward/backward command before starting
roboclaw.ForwardMixed(address, 0)
roboclaw.TurnRightMixed(address, 0)


# THIS CLASS IS TO IMPLEMENT AN EMERGENCY STOP BUTTON ON THE JOYPAD:
class buttons:
#buttons
    def __init__(self):
        self.subButtons = rospy.Subscriber("/joy", Joy, self.callback, queue_size = 10)
    #buttons handler
    def callback(self, msg):
        self.axes = msg.axes
        self.buttons = msg.buttons
        #X is used to activate input
        #self.X = self.buttons[0] 
        #self.A = self.buttons[1]
        #self.B = self.buttons[2]
        #self.Y = self.buttons[3]
        #self.LB = self.buttons[4]
        self.RB = self.buttons[5]
        #self.LT = self.buttons[6]
        #self.RT = self.buttons[7]
        #self.back = self.buttons[8]
        #self.start = self.buttons[9]
        self.emergencyStop();

    #emergency stop with Right Bumper
    #S3 on roboclaw is active low, so whenever its 0V then the roboclaw emegency stops
    def emergencyStop(self):
        gpioPort = 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpioPort, GPIO.OUT)
        GPIO.output(gpioPort, 1)
        if(self.RB == 1):
            print("EMERGENCY STOP - HOLD THE MOTOR SIDE UP AND FIDGET WITH JOYSTICK UNTIL STOP")
            GPIO.output(gpioPort, 0)

def cmdVelCB(twist):
    x = twist.linear.x
    z = twist.angular.z

    batteryVoltage = roboclaw.ReadMainBatteryVoltage(address)

    if(not batteryVoltage[0]):
        print("Checksum error, indicating signal issues")
    else:
        print("main battery voltage: " + str(batteryVoltage[1]/10) + " Volts")

    #make twist stay in bounds
    if(x > 0.2):
        x = 0.2
    elif(x < -0.2):
        x = -0.2

    if(z > ((1.57))):
        z = 1.57
    elif(z < (((-1.57)))):
        z = -1.57

    print(x, z)

    #creates linear speed from 0 - 127 and angular speed from 0 - 127
    #Valid data range is 0 - 127. 
    #A value of 0 = full backward, 64 = stop and 127 = full forward.
    #a value of 0 seems a little finicky so instead we put speed from 1 - 126 including 1 and 126
    speed = math.ceil(((x + 0.2)/0.4) * 126) + 1
    angle = math.ceil(((((1) * z * (360/math.pi)) + 180)/360) * 126) + 1
    print(speed, angle)

    #View if checcksum verification fails or succeeds
    error_1 = roboclaw.ForwardBackwardMixed(address, speed)
    error_2 = roboclaw.LeftRightMixed(address, angle)

    print(error_1, error_2)

    if((error_1 == False) or (error_2 == False)):
        roboclaw.ForwardBackwardMixed(address, 64)
        roboclaw.LeftRightMixed(address, 64)
   

   
def cmdUS(msg):
        sonic1 = msg[0]
        sonic2 = msg[1]
        sonic3 = msg[2]
        sonic4 = msg[3]
        '''
        while sonic1 <= 10:
                #A value of 0 = full backward, 64 = stop and 127 = full forward.
                roboclaw.ForwardBackwardMixed(address, 64)
                roboclaw.LeftRightMixed(address, 64)
                print("sonic 1: " + str(sonic1))
                time.sleep(5)
        while sonic2 <= 10:
                #A value of 0 = full backward, 64 = stop and 127 = full forward.
                roboclaw.ForwardBackwardMixed(address, 64)
                roboclaw.LeftRightMixed(address, 64)
                print("sonic 2: " + str(sonic2))
                time.sleep(5)
        while sonic3 <= 10:
                #A value of 0 = full backward, 64 = stop and 127 = full forward.
                roboclaw.ForwardBackwardMixed(address, 64)
                roboclaw.LeftRightMixed(address, 64)
                print("sonic 3: " + str(sonic3))
                time.sleep(5)
        while sonic4 <= 10:
                #A value of 0 = full backward, 64 = stop and 127 = full forward.
                roboclaw.ForwardBackwardMixed(address, 64)
                roboclaw.LeftRightMixed(address, 64)
                print("sonic 4: " + str(sonic4))
                time.sleep(5)
        '''



def processIMU_message(imuMsg):
    global yaw_offset

    roll=0
    pitch=0
    yaw=0

    quaternion = (
      imuMsg.orientation.x,
      imuMsg.orientation.y,
      imuMsg.orientation.z,
      imuMsg.orientation.w)
    (roll,pitch,yaw) = euler_from_quaternion(quaternion)

    #add align offset to yaw
    yaw += yaw_offset

    if(roll>10) :
        print("Roll>10, DROWNING\n")
        rospy.logerr("Roll>10, DROWNING\n")
    elif(pitch>10) :
        print("Pitch>10, DROWNING\n")
        rospy.logerr("Pitch>10, DROWNING\n")
    elif(yaw>10) :
        print("Yaw)10, DROWNING\n")
        rospy.logerr("Yaw>10, DROWNING\n")

def exit_handler():
    print('My application is ending!')
    ## 64 is the value used to make it stop
    roboclaw.ForwardBackwardMixed(address, 64)
    roboclaw.LeftRightMixed(address, 64)


########################################
########################################
########################################


    
if __name__ == '__main__':
    print("start")
    rospy.init_node('motor', anonymous=True)
    button_obj = buttons()
    rospy.Subscriber('cmd_vel', Twist, cmdVelCB)
    rospy.Subscriber('imu', Imu, processIMU_message)
    rospy.Subscriber('US', Float32, cmdUS)
    rospy.spin()

atexit.register(exit_handler)
