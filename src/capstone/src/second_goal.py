#!/usr/bin/env python3

import rospy
import geometry_msgs.msg as geometry_msgs
import tf
from tf.transformations import *

# --- waits for a user-defined goal and returns it. ---
def goal_subscriber():
    goal_pose = geometry_msgs.PoseStamped()
    goal_pose = rospy.wait_for_message("first_goal", geometry_msgs.PoseStamped, timeout = None)
    goal_pose.header.frame_id = "map"
    goal_pose.header.stamp = rospy.Time.now()
    return goal_pose

def second_goal(goal_pose):
    # https://stackoverflow.com/questions/70960130/given-a-position-and-rotation-how-can-i-find-a-point-that-extends-x-distance-fr

    # --- quaternion mulitplier 45 degrees (pi/4) ---
    #quaternion_rot = tf.transformations.quaternion_from_euler(0, 0, 1.5707)
    quaternion_rot = tf.transformations.quaternion_from_euler(0, 0, 0.78539816)

    # --- create quaternion from initial point's orientation ---
    initQuaternionX = goal_pose.pose.orientation.x
    initQuaternionY = goal_pose.pose.orientation.y 
    initQuaternionZ = goal_pose.pose.orientation.z  
    initQuaternionW = goal_pose.pose.orientation.w

    init_quaternion = [initQuaternionX, initQuaternionY, initQuaternionZ, initQuaternionW]

    # --- multiply initial quaternion by a 90 degree quaternion to rotate it 90 degrees ---
    q_new = quaternion_multiply(init_quaternion, quaternion_rot)

    # --- pass new pose orientation data to the goal to be published ---
    goal_pose.pose.orientation.x = q_new[0]
    goal_pose.pose.orientation.y = q_new[1]
    goal_pose.pose.orientation.z = q_new[2]
    goal_pose.pose.orientation.w = q_new[3]

    # --- while node is running, publish the new pose so it is visible on rviz ---
    while not rospy.is_shutdown():
        # rospy.loginfo(goal_pose)
        pub.publish(goal_pose)
        rate.sleep()

if __name__ == '__main__':
    rospy.init_node('second_goal', anonymous = True)
    pub = rospy.Publisher('/second_goal', geometry_msgs.PoseStamped, queue_size=10)
    # publish as geometry_msgs.PoseStamped so we can visualize in RViz. 
    # will need to convert this into MoveBaseGoal for action server when received
    rate = rospy.Rate(10)

    rospy.loginfo("Starting second_goal.py!")
    # --- wait for the user-defined goal ---
    goal_pose = goal_subscriber()

    rospy.sleep(5)

    # --- pass the user-defined goal to second_goal() to calculate the second goal ---
    second_goal(goal_pose)