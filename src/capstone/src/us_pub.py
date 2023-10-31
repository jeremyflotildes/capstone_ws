#!/usr/bin/python3
import rospy
from std_msgs.msg import Float32
import smbus
import time
from time import sleep          


ADDRESS_1 = 0x18 #(use 7-bit addressing)
ADDRESS_2 = 0x38
ADDRESS_3 = 0x30
ADDRESS_4 = 0x70
RANGE_CMD = 0x51 #81 decimal

bus = smbus.SMBus(1)    
time.sleep(1)


if __name__ == '__main__':
    pub1 = rospy.Publisher('US1', Float32, queue_size=10)
    pub2 = rospy.Publisher('US2', Float32, queue_size=10)
    pub3 = rospy.Publisher('US3', Float32, queue_size=10)
    pub4 = rospy.Publisher('US4', Float32, queue_size=10)
    rospy.init_node('Ultrasound', anonymous=True)
    rate=rospy.Rate(10)

    
    while not rospy.is_shutdown():
        
        bus.write_byte_data(ADDRESS_1, 0, RANGE_CMD)
        bus.write_byte_data(ADDRESS_2, 0, RANGE_CMD)
        bus.write_byte_data(ADDRESS_3, 0, RANGE_CMD)
        bus.write_byte_data(ADDRESS_4, 0, RANGE_CMD)
        sleep(1)

        
       #read 2 bytes
        dist1 = bus.read_i2c_block_data(ADDRESS_1, 1, 2) 
        dist2 = bus.read_i2c_block_data(ADDRESS_2, 1, 2)
        dist3 = bus.read_i2c_block_data(ADDRESS_3, 1, 2)
        dist4 = bus.read_i2c_block_data(ADDRESS_4, 1, 2)

        print ("Ultrasonic 1")
        print (dist1[1]/2.54)  ## turn into inches
        print ("\nUltrasonic 2")
        print (dist2[1]/2.54)
        print ("\nUltrasonic 3")
        print (dist3[1]/2.54)
        print ("\nUltrasonic 4")
        print (dist4[1]/2.54)
        print ("")
        print ("")

        us1 = dist1[1]/2.54
        us2 = dist2[1]/2.54
        us3 = dist3[1]/2.54
        us4 = dist4[1]/2.54

        pub1.publish(us1)
        pub2.publish(us2)
        pub3.publish(us3)
        pub4.publish(us4)
        rate.sleep()
