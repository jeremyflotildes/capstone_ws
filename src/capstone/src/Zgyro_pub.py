#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32

import smbus                    #import SMBus module of I2C
from time import sleep          #import
import numpy as np


#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38

GYRO_ZOUT_H  = 0x47


def shift(xs,n):
        if n>0:
            return np.concatenate((np.full(n,np.nan), xs[:-n]))
        else:
            return np.concatenate((xs[-n:], np.full(-n,np.nan)))
                

def MPU_Init():
        #write to sample rate register
        bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
        
        #Write to power management register
        bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
        
        #Write to Configuration register
        bus.write_byte_data(Device_Address, CONFIG, 0)
        
        #Write to Gyro configuration register
        bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
        
        #Write to interrupt enable register
        bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
        #Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value

#Filter stuff
n=5
Gyro=np.zeros(n,dtype='float')
wFltr=[1,1,10,1,1]
arrGyro=[]
arrFltrd=[]
x=[]


bus = smbus.SMBus(1)    # or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

if __name__ == '__main__':
    pub = rospy.Publisher('Zgyro', Float32, queue_size=10)
    rospy.init_node('Gyro', anonymous=True)
    rate=rospy.Rate(10)
    
    while not rospy.is_shutdown():
        #Read Gyroscope raw value
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        #Full scale range +/- 250 degree/C as per sensitivity scale factor
        Gz = .36+gyro_z/131.0

        #Filter it
        Gyro=shift(Gyro,1)
        Gyro[0]=Gz
        Fltrd_Rate=np.convolve(Gyro,wFltr,'valid')/10

        print ("Fltrd_Rate=%.3f" %Fltrd_Rate)
        #print (" " )

        if Fltrd_Rate>-.15 and Fltrd_Rate<.15:
                Fltrd_Rate=0.0

#        rospy.loginfo(Fltrd_Rate)
        pub.publish(Fltrd_Rate)
        rate.sleep()

