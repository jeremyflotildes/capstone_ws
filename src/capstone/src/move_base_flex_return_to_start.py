#!/usr/bin/env python

import actionlib
import rospy
import mbf_msgs.msg as mbf_msgs
import geometry_msgs.msg as geometry_msgs
import tf

# waits for a user-defined goal and returns it.
def goal_subscriber():
    goal_pose = rospy.wait_for_message("move_base_simple/goal", geometry_msgs.PoseStamped, timeout = None)
    rospy.loginfo("Received goal @ (%1.3f, %1.3f)", goal_pose.pose.position.x, goal_pose.pose.position.y)
    return goal_pose

#waits for the initial position of the robot and returns it.
def initial_pos_subscriber():
    rospy.loginfo("Listening for robot's initial transform...!")
    # create tf listener
    listener = tf.TransformListener()
    # set the node to run 1 time per second (1 hz)
    rate = rospy.Rate(1.0)
    # loop forever until roscore or this node is down
    valid_pose = False
    while valid_pose == False:
        try:
            # listen to transform
            (trans, rot) = listener.lookupTransform('/map', '/base_link', rospy.Time(0))
            # print the transform
            rospy.loginfo("Current position @ (%1.3f, %1.3f, %1.3f, %1.3f, %1.3f, %1.3f)", trans[0], trans[1], trans[2], rot[0], rot[1], rot[2])
            starting_pose = geometry_msgs.PoseStamped()
            starting_pose.pose.position.x = trans[0] 
            starting_pose.pose.position.y = trans[1]
            starting_pose.pose.position.z = trans[2]
            starting_pose.pose.orientation.x = rot[0]
            starting_pose.pose.orientation.y = rot[1]
            starting_pose.pose.orientation.z = rot[2]
            valid_pose = True
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue
        # sleep to control the node frequency
        rate.sleep()
        return starting_pose
    

def create_pose(x, y, z, xx, yy, zz, ww):
    pose = geometry_msgs.PoseStamped()
    pose.header.frame_id = "scanmatch_odom"
    pose.header.stamp = rospy.Time.now()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = z
    pose.pose.orientation.x = xx
    pose.pose.orientation.y = yy
    pose.pose.orientation.z = zz
    pose.pose.orientation.w = ww
    return pose


def create_path_goal(path, tolerance_from_action, dist_tolerance, angle_tolerance):
    goal = mbf_msgs.ExePathGoal()
    goal.path = path
    goal.tolerance_from_action = tolerance_from_action
    goal.dist_tolerance = dist_tolerance
    goal.angle_tolerance = angle_tolerance
    return goal


def exe_path(path_goal):
    mbf_ep_ac.send_goal(path_goal)
    mbf_ep_ac.wait_for_result()
    return mbf_ep_ac.get_result()


def get_plan(pose):
    path_goal = mbf_msgs.GetPathGoal(target_pose=pose, tolerance=0.5)
    mbf_gp_ac.send_goal(path_goal)
    mbf_gp_ac.wait_for_result()
    return mbf_gp_ac.get_result()


def goal_and_back(goal_pose):
        rospy.loginfo("Attempting to reach (%1.3f, %1.3f)", goal_pose.pose.position.x, goal_pose.pose.position.y)
        
        get_path_result = get_plan(goal_pose)
        if get_path_result.outcome != mbf_msgs.MoveBaseResult.SUCCESS:
            rospy.loginfo("Unable to complete plan: %s", result.message)
            success = False
            return success

        path_goal = create_path_goal(get_path_result.path, True, 0.5, 3.14/18.0)

        exe_path_result = exe_path(path_goal)
        if exe_path_result.outcome != mbf_msgs.MoveBaseResult.SUCCESS:
            rospy.loginfo("Unable to complete exe: %s", result.message)
            success = False
            return success


if __name__ == '__main__':
    rospy.init_node('get_goal', anonymous = True)

    # move_base_flex exe path client
    mbf_ep_ac = actionlib.SimpleActionClient("move_base_flex/exe_path", mbf_msgs.ExePathAction)
    mbf_ep_ac.wait_for_server(rospy.Duration(10))
    rospy.loginfo("Connected to Move Base Flex ExePath server!")

    # move base flex get path client
    mbf_gp_ac = actionlib.SimpleActionClient("move_base_flex/get_path", mbf_msgs.GetPathAction)
    mbf_gp_ac.wait_for_server(rospy.Duration(10))

    goal_pose = goal_subscriber()
    starting_pose = initial_pos_subscriber()

    success = goal_and_back(goal_pose)
    if success != False:
        goal_and_back(starting_pose)

    rospy.on_shutdown(lambda: mbf_ep_ac.cancel_all_goals())