#!/usr/bin/env python

import actionlib
import rospy
import mbf_msgs.msg as mbf_msgs
import geometry_msgs.msg as geometry_msgs
import tf
from tf.transformations import *


# waits for a user-defined goal and returns it.
def goal_subscriber():
    goal_pose = geometry_msgs.PoseStamped()
    goal_pose = rospy.wait_for_message("move_base_simple/goal", geometry_msgs.PoseStamped, timeout = None)
    goal_pose.header.frame_id = "map"
    goal_pose.header.stamp = rospy.Time.now()
    rospy.loginfo("Received goal @ (%1.3f, %1.3f)", goal_pose.pose.position.x, goal_pose.pose.position.y)
    return goal_pose

def second_goal(goal_pose):
    # https://stackoverflow.com/questions/70960130/given-a-position-and-rotation-how-can-i-find-a-point-that-extends-x-distance-fr
    # rotate current orientation 90 degrees
    quaternion_rot = tf.transformations.quaternion_from_euler(0, 0, 1.5707)
    distance = 1

    initQuaternionX = goal_pose.pose.orientation.x
    initQuaternionY = goal_pose.pose.orientation.y 
    initQuaternionZ = goal_pose.pose.orientation.z  
    initQuaternionW = goal_pose.pose.orientation.w

    init_quaternion = [initQuaternionX, initQuaternionY, initQuaternionZ, initQuaternionW]

    q_new = quaternion_multiply(init_quaternion, quaternion_rot)

    initX = goal_pose.pose.position.x
    initY = goal_pose.pose.position.y
    initZ = goal_pose.pose.position.z

    x = 0
    y = -2
    z = 0

    ix =   q_new[3] * x + q_new[1] * z - q_new[2] * y
    iy =   q_new[3] * y + q_new[2] * x - q_new[0] * z
    iz =   q_new[3] * z + q_new[0] * y - q_new[1] * x
    iw = - q_new[0] * x - q_new[1] * y - q_new[2] * z

    x = ix * q_new[3] + iw * - q_new[0] + iy * - q_new[2] - iz * - q_new[1]
    y = iy * q_new[3] + iw * - q_new[1] + iz * - q_new[0] - ix * - q_new[2]
    z = iz * q_new[3] + iw * - q_new[2] + ix * - q_new[1] - iy * - q_new[0]

    x = x * distance + initX
    y = y * distance + initY
    z = z * distance + initZ

    goal_pose.pose.orientation.x = q_new[0]
    goal_pose.pose.orientation.y = q_new[1]
    goal_pose.pose.orientation.z = q_new[2]
    goal_pose.pose.orientation.w = q_new[3]

    goal_pose.pose.position.x = x
    goal_pose.pose.position.y = y
    goal_pose.pose.position.z = z

    while not rospy.is_shutdown():
        rospy.loginfo(goal_pose)
        pub.publish(goal_pose)
        rate.sleep()

    """

    quaternion = tf.transformations.quaternion_from_euler(0, 0, -90)

    goal_pose.pose.orientation.x = quaternion[0]
    goal_pose.pose.orientation.y = quaternion[1]
    goal_pose.pose.orientation.z = quaternion[2]
    goal_pose.pose.orientation.w = quaternion[3]

    """

if __name__ == '__main__':
    rospy.init_node('second_goal', anonymous = True)
    pub = rospy.Publisher('/secondPoint', geometry_msgs.PoseStamped, queue_size=10)
    rate = rospy.Rate(10)

    rospy.loginfo("Starting second_goal.py!")
    goal_pose = goal_subscriber()
    second_goal(goal_pose)