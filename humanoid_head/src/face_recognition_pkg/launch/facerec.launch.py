from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='face_recognition_pkg',
            executable='face_node',
            name='face_node'
        )

    ])
