execute_process(COMMAND "/home/ubuntu/capstone_ws/build/py_trees_ros/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/ubuntu/capstone_ws/build/py_trees_ros/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
