# CMake generated Testfile for 
# Source directory: /home/ubuntu/capstone_ws/src/joystick_drivers/spacenav_node
# Build directory: /home/ubuntu/capstone_ws/build/spacenav_node
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(_ctest_spacenav_node_roslint_package "/home/ubuntu/capstone_ws/build/spacenav_node/catkin_generated/env_cached.sh" "/usr/bin/python3" "/opt/ros/noetic/share/catkin/cmake/test/run_tests.py" "/home/ubuntu/capstone_ws/build/spacenav_node/test_results/spacenav_node/roslint-spacenav_node.xml" "--working-dir" "/home/ubuntu/capstone_ws/build/spacenav_node" "--return-code" "/opt/ros/noetic/share/roslint/cmake/../../../lib/roslint/test_wrapper /home/ubuntu/capstone_ws/build/spacenav_node/test_results/spacenav_node/roslint-spacenav_node.xml make roslint_spacenav_node")
set_tests_properties(_ctest_spacenav_node_roslint_package PROPERTIES  _BACKTRACE_TRIPLES "/opt/ros/noetic/share/catkin/cmake/test/tests.cmake;160;add_test;/opt/ros/noetic/share/roslint/cmake/roslint-extras.cmake;67;catkin_run_tests_target;/home/ubuntu/capstone_ws/src/joystick_drivers/spacenav_node/CMakeLists.txt;19;roslint_add_test;/home/ubuntu/capstone_ws/src/joystick_drivers/spacenav_node/CMakeLists.txt;0;")
subdirs("gtest")
