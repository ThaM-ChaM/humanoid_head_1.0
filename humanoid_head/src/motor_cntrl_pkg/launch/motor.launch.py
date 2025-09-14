from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='motor_cntrl_pkg',
            executable='speech_sync',
            name='speech_sync'
        ),
        Node(
            package='motor_cntrl_pkg',
            executable='motor_command',
            name='motor_command'
        ),
        Node(
            package='motor_cntrl_pkg',
            executable='face_tracker',
            name='face_tracker'
        ),
        Node(
            package='motor_cntrl_pkg',
            executable='emotion_control',
            name='emotion_control'
        ),

    ])
