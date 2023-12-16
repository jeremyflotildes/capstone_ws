#!/usr/bin/env python3

import rospy
import geometry_msgs.msg as geometry_msgs
import std_msgs.msg as std_msgs
import tf
from tf.transformations import *

from math import cos, sin

# --- gets the distance from the robot to the wall on its left ---
def distance_subscriber():
    distance = std_msgs.Float32()
    distance = rospy.wait_for_message("laser_distance", std_msgs.Float32, timeout = None)
    return distance

# --- waits for a user-defined goal and returns it. ---
def goal_subscriber():
    goal_pose = geometry_msgs.PoseStamped()
    goal_pose = rospy.wait_for_message("third_goal", geometry_msgs.PoseStamped, timeout = None)
    goal_pose.header.frame_id = "map"
    goal_pose.header.stamp = rospy.Time.now()
    return goal_pose

def fourth_goal(goal_pose):
    # --- quaternion mulitplier 0 degrees (want to go straight) ---
    quaternion_rot = tf.transformations.quaternion_from_euler(0, 0, 0)

    # --- the distance away of the new point from initial point ---
    distance_msg = distance_subscriber()

    # --- create quaternion from initial point's orientation ---
    initQuaternionX = goal_pose.pose.orientation.x
    initQuaternionY = goal_pose.pose.orientation.y 
    initQuaternionZ = goal_pose.pose.orientation.z  
    initQuaternionW = goal_pose.pose.orientation.w

    init_quaternion = [initQuaternionX, initQuaternionY, initQuaternionZ, initQuaternionW]

    # --- multiply initial quaternion by a 90 degree quaternion to rotate it 90 degrees ---
    q_new = quaternion_multiply(init_quaternion, quaternion_rot)

    # --- save initial point's coordinates ---
    initX = goal_pose.pose.position.x
    initY = goal_pose.pose.position.y
    initZ = goal_pose.pose.position.z

    # --- calculate the new point along the new orientation, where variable x is the distance from the along this orientaion ---
    # y = 1.7 usually put the arrow a nice distance within the wall
    x = 1.7
    # x = distance_msg.data
    y = 0
    z = 0

    ix =   q_new[3] * x + q_new[1] * z - q_new[2] * y
    iy =   q_new[3] * y + q_new[2] * x - q_new[0] * z
    iz =   q_new[3] * z + q_new[0] * y - q_new[1] * x
    iw = - q_new[0] * x - q_new[1] * y - q_new[2] * z

    x = ix * q_new[3] + iw * - q_new[0] + iy * - q_new[2] - iz * - q_new[1]
    y = iy * q_new[3] + iw * - q_new[1] + iz * - q_new[0] - ix * - q_new[2]
    z = iz * q_new[3] + iw * - q_new[2] + ix * - q_new[1] - iy * - q_new[0]

    x = x + initX
    y = y + initY
    z = z + initZ

    # --- pass new pose orientation data to the goal to be published ---
    goal_pose.pose.orientation.x = q_new[0]
    goal_pose.pose.orientation.y = q_new[1]
    goal_pose.pose.orientation.z = q_new[2]
    goal_pose.pose.orientation.w = q_new[3]

     # --- pass new pose position data to the goal to be published ---
    goal_pose.pose.position.x = x
    goal_pose.pose.position.y = y
    goal_pose.pose.position.z = z

    # --- while node is running, publish the new pose so it is visible on rviz ---
    while not rospy.is_shutdown():
        # rospy.loginfo(goal_pose)
        pub.publish(goal_pose)
        rate.sleep()

if __name__ == '__main__':
    rospy.init_node('fourth_goal', anonymous = True)
    pub = rospy.Publisher('/fourth_goal', geometry_msgs.PoseStamped, queue_size=10)
    # publish as geometry_msgs.PoseStamped so we can visualize in RViz. 
    # will need to convert this into MoveBaseGoal for action server when received
    rate = rospy.Rate(10)

    rospy.loginfo("Starting fourth_goal.py!")
    # --- wait for the user-defined goal ---
    goal_pose = goal_subscriber()

    rospy.sleep(5)

    # --- pass the user-defined goal to fourth_goal() to calculate the fourth goal ---
    fourth_goal(goal_pose)