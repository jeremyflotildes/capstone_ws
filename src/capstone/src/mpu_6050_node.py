#!/usr/bin/python3
import smbus
import time
import struct
import rospy
import numpy as np
from sensor_msgs.msg import Temperature, Imu
from tf.transformations import quaternion_about_axis
import RPi.GPIO as gpio

 
#register values
PWR_M   = 0x6B

DIV   = 0x19

CONFIG       = 0x1A

GYRO_CONFIG  = 0x1B

INT_EN   = 0x38

ACCEL_X = 0x3B

ACCEL_Y = 0x3D

ACCEL_Z = 0x3F

GYRO_X  = 0x43

GYRO_Y  = 0x45

GYRO_Z  = 0x47

TEMP = 0x41


bus = smbus.SMBus(1)

Device_Address = 0x68   # device address

IMU_FRAME = None

 
#intial acceleration and gyro values
AxCal=0

AyCal=0

AzCal=0

GxCal=0

GyCal=0

GzCal=0



Ax=0

Ay=0

Az=0

Gx=0

Gy=0

Gz=0
 

gpio.setwarnings(False)

gpio.setmode(gpio.BCM)

IMU_FRAME = None
 

 

def InitMPU():

    bus.write_byte_data(Device_Address, DIV, 7)

    bus.write_byte_data(Device_Address, PWR_M, 1)

    bus.write_byte_data(Device_Address, CONFIG, 0)

    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    bus.write_byte_data(Device_Address, INT_EN, 1)

    time.sleep(1)

 

def readMPU(addr):

  high = bus.read_byte_data(Device_Address, addr)

  low = bus.read_byte_data(Device_Address, addr+1)

  value = ((high << 8) | low)

  if(value > 32768):

    value = value - 65536

  return value

def publish_imu():
  imu_msg = Imu()
  imu_msg.header.frame_id = IMU_FRAME

  # Read the acceleration vals
  x = readMPU(ACCEL_X)
  y = readMPU(ACCEL_Y)
  z = readMPU(ACCEL_Z)

  # adjust acceleration vals with offsets
  Ax = (x/16384.0-AxCal) 
  Ay = (y/16384.0-AyCal) 
  Az = (z/16384.0-AzCal)

  # Calculate a quaternion representing the orientation
  accel = Ax, Ay, Az
  ref = np.array([0, 0, 1])
  acceln = accel / np.linalg.norm(accel)
  axis = np.cross(acceln, ref)
  angle = np.arccos(np.dot(acceln, ref))
  orientation = quaternion_about_axis(angle, axis)

  x1 = readMPU(GYRO_X)
  y1 = readMPU(GYRO_Y)
  z1 = readMPU(GYRO_Z)

  Gx = x1/131.0 - GxCal
  Gy = y1/131.0 - GyCal
  Gz = z1/131.0 - GzCal

  # Load up the IMU message
  o = imu_msg.orientation
  o.x, o.y, o.z, o.w = orientation

  imu_msg.linear_acceleration.x = Ax
  imu_msg.linear_acceleration.y = Ay
  imu_msg.linear_acceleration.z = Az

  imu_msg.angular_velocity.x = Gx
  imu_msg.angular_velocity.y = Gy
  imu_msg.angular_velocity.z = Gz

  imu_msg.header.stamp = rospy.Time.now()

  imu_pub.publish(imu_msg)
 

def gyro():

  global GxCal

  global GyCal

  global GzCal

  x = readMPU(GYRO_X)

  y = readMPU(GYRO_Y)

  z = readMPU(GYRO_Z)

  Gx = x/131.0 - GxCal

  Gy = y/131.0 - GyCal

  Gz = z/131.0 - GzCal

  print("Gx ", Gx)
  print("Gy ", Gy)
  print("Gz ", Gz)
  print(" ")
  print(" ")

  #print "X="+str(Gx)
  publish_imu()
  time.sleep(1)

 

def temp(timer_event):
  temp_msg = Temperature()
  temp_msg.header.frame_id = IMU_FRAME

  tempRow=readMPU(TEMP)

  temp_msg.temperature = (tempRow / 340.0) + 36.53
  temp_msg.header.stamp = rospy.Time.now()
  temp_pub.publish(temp_msg)
 
#calibration by sampling values whilw the robot is in place
#then normalizing and using that as an offset.
def calibrate():

  global AxCal

  global AyCal

  global AzCal

  x=0

  y=0

  z=0

  #60 seconds multiplied by minutes = minutes of time to calibrate
  #change the line below to calibrate longer or for less time
  calibrationTime = 10 #60*1
  for i in range(calibrationTime):

      x = x + readMPU(ACCEL_X)

      y = y + readMPU(ACCEL_Y)

      #subtract when upside down
      #add when right side up
      z = z - readMPU(ACCEL_Z)

      time.sleep(1)
  

  x= x/calibrationTime 

  y= y/calibrationTime 

  z= z/calibrationTime 

  AxCal = x/16384.0

  AyCal = y/16384.0

  AzCal = (16384.0-z)/16384.0

  

  #print("AxCal", AxCal)

  #print("AyCal", AyCal)

  #print("AzCal", AzCal)

 

  global GxCal

  global GyCal

  global GzCal

  x=0

  y=0

  z=0

  for i in range(50):

    x = x + readMPU(GYRO_X)

    y = y + readMPU(GYRO_Y)

    z = z + readMPU(GYRO_Z)

  x= x/50

  y= y/50

  z= z/50

  GxCal = x/131.0

  GyCal = y/131.0

  GzCal = z/131.0

 

  #print("GxCal: ", GxCal)

  #print("GyCal", GyCal)

  #print("GzCal", GzCal)

 

 

time.sleep(2)
print ("Init IMU")
InitMPU()

print("cal")
calibrate()

if __name__ == '__main__':

  print ("RUNNING")
  imu_pub = rospy.Publisher('imu_data', Imu, queue_size=10)
  rospy.init_node('imu_node')
  rate=rospy.Rate(10)
  while not rospy.is_shutdown():
    gyro()
    rate.sleep()
