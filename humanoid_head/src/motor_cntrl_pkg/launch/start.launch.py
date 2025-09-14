from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription
import os

def generate_launch_description():
    # Example for including two launch files from two different packages
    conversation_pkg = 'robot_conversation_pipeline'
    face_rec_pkg = 'face_recognition_pkg'
    motor_control_pkg = 'motor_cntrl_pkg'

    launch_file1 = os.path.join(
        FindPackageShare(conversation_pkg).find(conversation_pkg),
        'launch',
        'conversation.launch.py'
    )

    launch_file2 = os.path.join(
        FindPackageShare(face_rec_pkg).find(face_rec_pkg),
        'launch',
        'facerec.launch.py'
    )

    launch_file3 = os.path.join(
        FindPackageShare(motor_control_pkg).find(motor_control_pkg),
        'launch',
        'motor.launch.py'
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file1)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file2)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file3)
        )
    ])
