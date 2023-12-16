#! /usr/bin/env python3

import rospy
import sensor_msgs.msg as sensor_msgs
from tf.transformations import *
import std_msgs.msg as std_msgs

# subscribes to the laser scan topic in order to get the distances
# 780 total points in the laser scan. 0 -> 780 clockwise.
def laser_subscriber():
    laser = sensor_msgs.LaserScan()
    sum = 0
    sum_of_avg = 0
    for i in range(0, 100): # get the range on the left side of the robot 100 times and average it out for a final value
        laser = rospy.wait_for_message("scan", sensor_msgs.LaserScan, timeout = None)
        for i in range(560, 610): # iterate thru this range of data which represents the left side of the laser scan
            if laser.ranges[i] != float('inf'):
                sum += laser.ranges[i]
        avg = sum / 50
        sum = 0
        sum_of_avg += avg
    avg_of_avg = sum_of_avg / 100
    rospy.loginfo("Done averaging laser distances!")

    # need to make distance smaller as the robot will turn towards and will need to cover less distance
    avg_of_avg -= 0.68
    rospy.loginfo(avg_of_avg)

    # create Int32 msg to publish the average distance of the wall away
    msg = std_msgs.Float32()
    msg.data = avg_of_avg

    # --- while node is running, publish the new pose so it is visible on rviz ---
    while not rospy.is_shutdown():
        # rospy.loginfo(goal_pose)
        pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    rospy.init_node('laser_subscriber')
    pub = rospy.Publisher('/laser_distance', std_msgs.Float32, queue_size=10)
    rate = rospy.Rate(10)

    laser_subscriber()