#! /usr/bin/env python3

import rospy
import actionlib
import geometry_msgs.msg as geometry_msgs
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import *

# -- converts geometry_msgs.PoseStamped, a message that allows us to visualize goals on RViz, to MoveBaseGoal(),
# a message that can be sent to the ActionServer for the robot to act upon --
def pose_to_goal(pose, goal):
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    goal.target_pose.pose.position.x = pose.pose.position.x
    goal.target_pose.pose.position.y = pose.pose.position.y
    goal.target_pose.pose.position.z = pose.pose.position.z

    goal.target_pose.pose.orientation.x = pose.pose.orientation.x
    goal.target_pose.pose.orientation.y = pose.pose.orientation.y
    goal.target_pose.pose.orientation.z = pose.pose.orientation.z
    goal.target_pose.pose.orientation.w = pose.pose.orientation.w
    return goal

# --- waits for a user-defined goal and returns it. ---
def goal_subscriber():
    first_pose = geometry_msgs.PoseStamped()
    first_pose = rospy.wait_for_message("first_goal", geometry_msgs.PoseStamped, timeout = None)

    goal = MoveBaseGoal()
    goal = pose_to_goal(first_pose, goal)
    return goal

# --- waits for the second goal and returns it ---
def second_goal():
    second_pose = geometry_msgs.PoseStamped()
    second_pose = rospy.wait_for_message("second_goal", geometry_msgs.PoseStamped, timeout = None)

    goal = MoveBaseGoal()
    goal = pose_to_goal(second_pose, goal)
    return goal

# --- waits for the third goal and returns it ---
def third_goal():
    third_pose = geometry_msgs.PoseStamped()
    third_pose = rospy.wait_for_message("third_goal", geometry_msgs.PoseStamped, timeout = None)

    goal = MoveBaseGoal()
    pose_to_goal(third_pose, goal)
    return goal

# --- waits for the fourth goal and returns it ---
def fourth_goal():
    fourth_pose = geometry_msgs.PoseStamped()
    fourth_pose = rospy.wait_for_message("fourth_goal", geometry_msgs.PoseStamped, timeout = None)

    goal = MoveBaseGoal()
    goal = pose_to_goal(fourth_pose, goal)
    return goal

# --- waits for the fifth goal and returns it ---
def fifth_goal():
    fifth_goal = geometry_msgs.PoseStamped()
    fifth_goal = rospy.wait_for_message("fifth_goal", geometry_msgs.PoseStamped, timeout = None)

    goal = MoveBaseGoal()
    goal = pose_to_goal(fifth_goal, goal)
    return goal

# --- waits for the sixth goal and returns it ---
def sixth_goal():
    sixth_goal = geometry_msgs.PoseStamped()
    sixth_goal = rospy.wait_for_message("sixth_goal", geometry_msgs.PoseStamped, timeout = None)

    goal = MoveBaseGoal()
    goal = pose_to_goal(sixth_goal, goal)
    return goal


def done_cb(status, result):
    # Reference for terminal status values: http://docs.ros.org/diamondback/api/actionlib_msgs/html/msg/GoalStatus.html
    if status == 2:
        rospy.loginfo("Goal pose received a cancel request after it started executing, completed execution!")

    if status == 3:
        rospy.loginfo("Goal pose reached.")

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
        
    return status


if __name__ == '__main__':
    rospy.init_node('waypoints')

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

    # Waits until the action server has started up and started
    # listening for goals.
    rospy.loginfo("Starting up action server...")
    client.wait_for_server()
    rospy.loginfo("Action server started!")

    rospy.loginfo("Waiting for the first goal...")    
    # wait for the first, user-defined goal and send it
    first_goal = goal_subscriber()
    rospy.loginfo("First goal received!")
    client.send_goal(first_goal, done_cb)
    rospy.loginfo("First goal sent!")
    # Waits for the server to finish performing the action.
    client.wait_for_result()
    # Sleep briefly to allow robot to settle in
    rospy.sleep(3) 

    # Creates a goal to send to the action server.
    rospy.loginfo("Creating second goal to turn 45 degrees towards the opposite wall.")
    second_goal = second_goal()
    rospy.loginfo("Second goal received!")
    # Sends the goal to the action server.
    client.send_goal(second_goal, done_cb)
    rospy.loginfo("Second goal sent!")
    client.wait_for_result()
    rospy.sleep(3)

    rospy.loginfo("Creating third goal to turn another 45 degrees towards the opposite wall.")
    third_goal = third_goal()
    rospy.loginfo("Third goal received!")
    # Sends the goal to the action server.
    client.send_goal(third_goal, done_cb)
    rospy.loginfo("Third goal sent!")
    client.wait_for_result()
    rospy.sleep(3) 

    rospy.loginfo("Creating fourth goal across the hallway.")
    fourth_goal = fourth_goal()
    rospy.loginfo("Fourth goal received!")
    # Sends the goal to the action server.
    client.send_goal(fourth_goal, done_cb)
    rospy.loginfo("Fourth goal sent!")
    client.wait_for_result()
    rospy.sleep(3)

    rospy.loginfo("Creating fifth goal to turn another 45 degrees to be parallel with the wall.")
    fifth_goal = fifth_goal()
    rospy.loginfo("Fifth goal received!")
    # Sends the goal to the action server.
    client.send_goal(fifth_goal, done_cb)
    rospy.loginfo("Fifth goal sent!")
    client.wait_for_result()
    rospy.sleep(3)

    rospy.loginfo("Creating sixth goal to turn another 45 degrees to be parallel with the wall.")
    sixth_goal = sixth_goal()
    rospy.loginfo("Sixth goal received!")
    # Sends the goal to the action server.
    client.send_goal(sixth_goal, done_cb)
    rospy.loginfo("Sixth goal sent!")
    client.wait_for_result()
    rospy.sleep(3)  