# first arg
string_raw=$1

cd /home/jgorka/catkin_fastlio_slam
python fixbag_pawel.py $string_raw
string_repaired=${string_raw/.bag/-repaired.bag}

# start roscore
cd /home/jgorka/catkin_ws
source ./devel/setup.bash
roslaunch fast_lio mapping_avia.launch &
PID1=$!
sleep 2 

# start rosbag play
# here put rosbag
cd /home/jgorka/catkin_fastlio_slam
rosbag play $string_repaired 
PID2=$!
sleep 2


kill $PID1
kill $PID2

sleep 15

# move to export folder
mv /home/jgorka/catkin_ws/src/FAST_LIO/PCD/scans.pcd /home/jgorka/Desktop/export/${string_raw/bag/pcd}
mv /home/jgorka/catkin_ws/src/FAST_LIO/Log/pos_log.txt /home/jgorka/Desktop/export/${string_raw/bag/txt}
