# from launch import LaunchDescription
# from launch_ros.actions import Node

# def generate_launch_description():
#     return LaunchDescription([
#         Node(
#             package='robot_conversation_pipeline',
#             executable='audio_recorder',
#             name='audio_recorder'
#         ),
#         Node(
#             package='robot_conversation_pipeline',
#             executable='audio_transcription',
#             name='audio_transcription'
#         ),
#         Node(
#             package='robot_conversation_pipeline',
#             executable='server_communication',
#             name='server_communication'
#         ),
#         Node(
#             package='robot_conversation_pipeline',
#             executable='emotion_monitor',
#             name='emotion_monitor'
#         ),
#         Node(
#             package='robot_conversation_pipeline',
#             executable='audio_retrieval',
#             name='audio_retrieval'
#         )
#     ])

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Other nodes start immediately
        Node(
            package='robot_conversation_pipeline',
            executable='audio_transcription',
            name='audio_transcription'
        ),
        Node(
            package='robot_conversation_pipeline',
            executable='server_communication',
            name='server_communication'
        ),
        Node(
            package='robot_conversation_pipeline',
            executable='emotion_monitor',
            name='emotion_monitor'
        ),
        Node(
            package='robot_conversation_pipeline',
            executable='audio_retrieval',
            name='audio_retrieval'
        ),

        # Delayed launch of audio_recorder (e.g., after 15 seconds)
        TimerAction(
            period=15.0,
            actions=[
                Node(
                    package='robot_conversation_pipeline',
                    executable='audio_recorder',
                    name='audio_recorder'
                )
            ]
        )
    ])
