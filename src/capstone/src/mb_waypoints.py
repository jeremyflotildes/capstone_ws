#! /usr/bin/env python3

import rospy
import actionlib
import mbf_msgs.msg as mbf_msgs
import geometry_msgs.msg as geometry_msgs
import tf
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import *

# --- waits for a user-defined goal and returns it. ---
def goal_subscriber():
    first_goal = geometry_msgs.PoseStamped()
    first_goal = rospy.wait_for_message("move_base_simple/goal", geometry_msgs.PoseStamped, timeout = None)

    goal_pose = MoveBaseGoal()
    goal_pose.target_pose.header.frame_id = "map"
    goal_pose.target_pose.header.stamp = rospy.Time.now()

    goal_pose.target_pose.pose.position.x = first_goal.pose.position.x
    goal_pose.target_pose.pose.position.y = first_goal.pose.position.y
    goal_pose.target_pose.pose.position.z = first_goal.pose.position.z

    goal_pose.target_pose.pose.orientation.x = first_goal.pose.orientation.x
    goal_pose.target_pose.pose.orientation.y = first_goal.pose.orientation.y
    goal_pose.target_pose.pose.orientation.z = first_goal.pose.orientation.z
    goal_pose.target_pose.pose.orientation.w = first_goal.pose.orientation.w

    rospy.loginfo("Received FIRST goal @ (%1.3f, %1.3f)", goal_pose.target_pose.pose.position.x, goal_pose.target_pose.pose.position.y)
    return goal_pose

def second_goal(goal_pose):
    # https://stackoverflow.com/questions/70960130/given-a-position-and-rotation-how-can-i-find-a-point-that-extends-x-distance-fr

    # --- quaternion mulitplier 90 degrees (pi/2) ---
    quaternion_rot = tf.transformations.quaternion_from_euler(0, 0, 1.5707)

    # --- the distance away of the new point from initial point ---
    distance = 1

    # --- create quaternion from initial point's orientation ---
    initQuaternionX = goal_pose.target_pose.pose.orientation.x
    initQuaternionY = goal_pose.target_pose.pose.orientation.y 
    initQuaternionZ = goal_pose.target_pose.pose.orientation.z  
    initQuaternionW = goal_pose.target_pose.pose.orientation.w

    init_quaternion = [initQuaternionX, initQuaternionY, initQuaternionZ, initQuaternionW]

    # --- multiply initial quaternion by a 90 degree quaternion to rotate it 90 degrees ---
    q_new = quaternion_multiply(init_quaternion, quaternion_rot)

    # --- save initial point's coordinates ---
    initX = goal_pose.target_pose.pose.position.x
    initY = goal_pose.target_pose.pose.position.y
    initZ = goal_pose.target_pose.pose.position.z

    # --- calculate the new point ---
    x = 0
    y = -1
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

    # --- pass new pose orientation data to the goal to be published ---
    goal_pose.target_pose.pose.orientation.x = q_new[0]
    goal_pose.target_pose.pose.orientation.y = q_new[1]
    goal_pose.target_pose.pose.orientation.z = q_new[2]
    goal_pose.target_pose.pose.orientation.w = q_new[3]

     # --- pass new pose position data to the goal to be published ---
    goal_pose.target_pose.pose.position.x = x
    goal_pose.target_pose.pose.position.y = y
    goal_pose.target_pose.pose.position.z = z
    rospy.loginfo("Received SECOND goal @ (%1.3f, %1.3f)", goal_pose.target_pose.pose.position.x, goal_pose.target_pose.pose.position.y)
    return goal_pose

def done_cb(status, result):
    # Reference for terminal status values: http://docs.ros.org/diamondback/api/actionlib_msgs/html/msg/GoalStatus.html
        if status == 2:
            rospy.loginfo("Goal pose received a cancel request after it started executing, completed execution!")

        if status == 3:
            rospy.loginfo("Goal pose reached") 

        if status == 4:
            rospy.loginfo("Goal pose was aborted by the Action Server")
            rospy.signal_shutdown("Goal pose aborted, shutting down!")
            return

        if status == 5:
            rospy.loginfo("Goal pose has been rejected by the Action Server")
            rospy.signal_shutdown("Goal pose rejected, shutting down!")
            return

        if status == 8:
            rospy.loginfo("Goal pose received a cancel request before it started executing, successfully cancelled!")


if __name__ == '__main__':
    rospy.init_node('fibonacci_client_py')

    starting_goal = goal_subscriber()

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

    # Waits until the action server has started up and started
    # listening for goals.
    rospy.loginfo("Starting up action server...")
    client.wait_for_server()
    rospy.loginfo("Action server started!")

    # Creates a goal to send to the action server.
    #second_goal = second_goal(starting_goal)
    
    rospy.loginfo("Sent second goal to action server!")
    # Sends the goal to the action server.
    client.send_goal(second_goal, done_cb)

    # Waits for the server to finish performing the action.
    client.wait_for_result()
