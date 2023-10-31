#! /usr/bin/env python3

import rospy
import actionlib
from extended_object_detection.msg import SimpleObjectArray
from geometry_msgs.msg import PoseStamped, Transform, Vector3
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

class move_to_object:
    def __init__(self):

        #subscribers -> from the camera, subscribe to detected simple object
        #when extended_object_detection sees a simple object it will publish it to this topic
        #self.callback -> when it recieves a message, the function callback will be called
        rospy.Subscriber("/extended_object_detection/simple_objects", SimpleObjectArray, self.callback)

        #initial conditions
        self.simple_object = SimpleObjectArray()    #entire message of simple-objects, array
        self.pose_x = 0                             #initial value for position in x direction
        self.pose_y = 0                             #initial value for position in y direction
        goal = MoveBaseGoal()                       #goal variable, set up as a MoveBaseGoal so move_base will accept the format

    #callback function
    def callback(self, msg):
        #simple_object will hold the objects part of the recieved message
        self.simple_object = msg.objects

        #if the name of the simple object in array position 0 (the closest detected object) is redPost it
        if self.simple_object[0].name == "redPostIt":
            #set x position variable as x position of object
            self.pose_x = self.simple_object[0].transform.translation.x
            # set x position variable as x position of object
            self.pose_y = self.simple_object[0].transform.translation.y
            #use x and y values in move_to_object function
            move_to_object(self.pose_x, self.pose_y)

    #move_to_object function
    def move_to_object(self, x, y)

        #make move_base goal -> target_pose.pose.position.x is a subset of MoveBaseGoal() for the x position value
        goal.target_pose.pose.position.x = x
        #same as above but with y position value
        goal.target_pose.pose.orientation.y = y

        #sends the goal to the move_base action server
        client.send_goal(goal)
        #waits for the server to finish performing the action
        wait = client.wait_for_result()

#main function
if __name__=='__main__':
    #initialize the ROS node (which is the program here, called a node)
    rospy.init_node('move_to_object', anonymous=True)
    #start class
    move_to_object()
    #loops this node until its shutdown
    rospy.spin()
