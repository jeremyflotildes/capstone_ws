#! /usr/bin/env python3

from math import sqrt
import rospy
import sensor_msgs.msg as sensor_msgs
import geometry_msgs.msg as geometry_msgs
from tf.transformations import *
import std_msgs.msg as std_msgs

# subscribes to initial pose position and user-define goal position
def position_subscriber():

    # waits for a user-defined goal and returns it.
    goal_pose = geometry_msgs.PoseStamped()
    goal_pose = rospy.wait_for_message("first_goal", geometry_msgs.PoseStamped, timeout = None)
    goal_pose.header.frame_id = "map"
    goal_pose.header.stamp = rospy.Time.now()
    rospy.loginfo("Received goal @ (%1.3f, %1.3f)", goal_pose.pose.position.x, goal_pose.pose.position.y)

    # get initial pose
    starting_pose = geometry_msgs.PoseWithCovarianceStamped()
    starting_pose = rospy.wait_for_message("/amcl_pose", geometry_msgs.PoseWithCovarianceStamped, timeout=None)
    rospy.loginfo("Initial Position @ (%1.3f, %1.3f)", starting_pose.pose.pose.position.x, starting_pose.pose.pose.position.y)

    #apply distance formula between two points
    x_squared = (goal_pose.pose.position.x - starting_pose.pose.pose.position.x)**2
    y_squared = (goal_pose.pose.position.y - starting_pose.pose.position.y)**2
    distance = sqrt(x_squared + y_squared)

     # create Int32 msg to publish the average lenght of the wall to be swept
    msg = std_msgs.Float32()
    msg.data = distance

    # --- while node is running, publish the new pose so it is visible on rviz ---
    while not rospy.is_shutdown():
        # rospy.loginfo(goal_pose)
        pub.publish(msg)
        rate.sleep()


if __name__ == '__main__':
    rospy.init_node('opposite_wall_distance')
    pub = rospy.Publisher('/opposite_wall_distance', std_msgs.Float32, queue_size=10)
    rate = rospy.Rate(10)

    position_subscriber()