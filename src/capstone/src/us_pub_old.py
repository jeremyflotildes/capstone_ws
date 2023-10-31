#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32
import smbus
from time import sleep          


ADDRESS = 0x38  #(use 7-bit addressing)
RANGE_CMD = 0x51 #81 decimal

bus = smbus.SMBus(1)    

if __name__ == '__main__':
    pub = rospy.Publisher('LFUS', Float32, queue_size=10)
    rospy.init_node('Ultrasound', anonymous=True)
    rate=rospy.Rate(10)
    print("Statred")
    while not rospy.is_shutdown():
        
        bus.write_byte_data(ADDRESS, 0, RANGE_CMD)

        sleep(1)
        
        #read 2 bytes
        dist = bus.read_i2c_block_data(ADDRESS, 1, 2)

        print(dist[1]/2.5) #turn into inches

        pub.publish(dist[1])
        rate.sleep()

