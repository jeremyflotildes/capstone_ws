#!/usr/bin/python3

import rospy
import pigpio

if __name__ == '__main__':
    rospy.init_node('pwm_test')
    pi=pigpio.pi()
    for n in range(0, 1000000, 10):
        print(n)
        pi.hardware_PWM(13, 20000, n)
    pi.hardware_PWM(13, 20000, 0)
    pi.stop()