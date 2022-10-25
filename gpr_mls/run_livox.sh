cd /home/jgorka/catkin_fastlio_slam
source ./devel/setup.bash
roscore &
sleep 2
roslaunch fast_lio mapping_avia.launch &
sleep 2 
roslaunch livox_ros_driver livox_lidar_msg.launch &
sleep 2
rosbag record -a -o session.bag
