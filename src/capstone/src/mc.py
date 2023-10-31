#!/usr/bin/env python3

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
rad2degrees = 180.0/math.pi
precision = 2 #round to this number of digits

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#  L298N H-Bridge

#-----------------   Define Motor Driver GPIO Pins   ---------------
#   Left Side GPIO CONSTANTS

PWM_DRIVE_LEFT = 20	      # 38 PWM, ENA - H-Bridge enable pin
FORWARD_LEFT_PIN = 6	       # 31 IN1 - Forward Drive
REVERSE_LEFT_PIN = 13	       # 33 IN2 - Reverse Drive

#  Right Side GPIO CONSTANTS

PWM_DRIVE_RIGHT = 21	       # 40 PWM, ENB - H-Bridge enable pin
FORWARD_RIGHT_PIN = 19	# 35 IN1 - Forward Drive
REVERSE_RIGHT_PIN = 26	# 37 IN2 - Reverse Drive

#--------------------------------------------------------

#-----------------   Define Motor Driver GPIO Pins   ---------------

GPIO.setup(PWM_DRIVE_LEFT, GPIO.OUT)
GPIO.setup(FORWARD_LEFT_PIN, GPIO.OUT)
GPIO.setup(REVERSE_LEFT_PIN, GPIO.OUT)

GPIO.setup(PWM_DRIVE_RIGHT, GPIO.OUT)
GPIO.setup(FORWARD_RIGHT_PIN, GPIO.OUT)
GPIO.setup(REVERSE_RIGHT_PIN, GPIO.OUT)

#--------------------------------------------------------


#-----------------   Initialize GPIO Pins   ---------------

driveLeft = GPIO.PWM(PWM_DRIVE_LEFT, 100) 
driveLeft.start(0)
driveRight = GPIO.PWM(PWM_DRIVE_RIGHT, 100)  
driveRight.start(0)

GPIO.output(FORWARD_RIGHT_PIN, GPIO.HIGH)
GPIO.output(REVERSE_RIGHT_PIN, GPIO.LOW)
GPIO.output(FORWARD_LEFT_PIN, GPIO.HIGH)
GPIO.output(REVERSE_LEFT_PIN, GPIO.LOW)

#--------------------------------------------------------


########################################
########################################
########################################


def cmdVelCB(twist):
	left_wheel_data = 5*twist.linear.x - twist.angular.z
	right_wheel_data = 5*twist.linear.x + twist.angular.z

	print(right_wheel_data, left_wheel_data)

	if(right_wheel_data <= 0):
		GPIO.output(FORWARD_RIGHT_PIN, GPIO.HIGH)
		GPIO.output(REVERSE_RIGHT_PIN, GPIO.LOW)
		driveRight.ChangeDutyCycle(100*(min(abs(right_wheel_data),1))) 

	else:
		GPIO.output(FORWARD_RIGHT_PIN, GPIO.LOW)
		GPIO.output(REVERSE_RIGHT_PIN, GPIO.HIGH)
		driveRight.ChangeDutyCycle(100*(min(abs(right_wheel_data),1))) 


	if(left_wheel_data <= 0):
		GPIO.output(FORWARD_LEFT_PIN, GPIO.LOW)
		GPIO.output(REVERSE_LEFT_PIN, GPIO.HIGH)
		driveLeft.ChangeDutyCycle(100*(min(abs(left_wheel_data),1))) 

	else:
		GPIO.output(FORWARD_LEFT_PIN, GPIO.HIGH)
		GPIO.output(REVERSE_LEFT_PIN, GPIO.LOW)
		driveLeft.ChangeDutyCycle(100*(min(abs(left_wheel_data),1))) 

   

   
def cmdUS(msg):
        sonic1 = msg[0]
        sonic2 = msg[1]
        sonic3 = msg[2]
        sonic4 = msg[3]
        while sonic1 <= 10:
                GPIO.output(FORWARD_RIGHT_PIN, GPIO.LOW)
                GPIO.output(REVERSE_LEFT_PIN, GPIO.LOW)
                time.sleep(5)
        while sonic2 <= 10:
                GPIO.output(FORWARD_RIGHT_PIN, GPIO.LOW)
                GPIO.output(REVERSE_LEFT_PIN, GPIO.LOW)
                time.sleep(5)
        while sonic3 <= 10:
                GPIO.output(FORWARD_RIGHT_PIN, GPIO.LOW)
                GPIO.output(REVERSE_LEFT_PIN, GPIO.LOW)
                time.sleep(5)
        while sonic4 <= 10:
                GPIO.output(FORWARD_RIGHT_PIN, GPIO.LOW)
                GPIO.output(REVERSE_LEFT_PIN, GPIO.LOW)
                time.sleep(5)



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


########################################
########################################
########################################


    
if __name__ == '__main__':
    print("start")
    rospy.init_node('motor', anonymous=True)
    rospy.Subscriber('cmd_vel', Twist, cmdVelCB)
    ##rospy.Subscriber('imu', Imu, cmdIMU)
    rospy.Subscriber('imu', Imu, processIMU_message)
    #commented out cmdUS OCT 31 2022 because it was being annoying
    #rospy.Subscriber('US', Float32, cmdUS)
    rospy.spin()
