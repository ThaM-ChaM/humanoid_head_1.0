from setuptools import setup
import os
from glob import glob

package_name = 'robot_conversation_pipeline'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kuweni',
    maintainer_email='kuweni@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 'audio_recorder_with_directions = robot_conversation_pipeline.audio_recorder_node_with_directions_v1:main',
            'audio_recorder = robot_conversation_pipeline.audio_recorder_node:main',
            'audio_recorder_v2 = robot_conversation_pipeline.audio_recorder_v2_node:main',
            'speech_seperator = robot_conversation_pipeline.speech_separation_v2_node:main',
            'audio_retrieval = robot_conversation_pipeline.audio_retrieval_node:main',
            'audio_transcription = robot_conversation_pipeline.audio_transcription_node:main',
            'emotion_monitor = robot_conversation_pipeline.emotion_monitor_node:main',
            'server_communication = robot_conversation_pipeline.server_communication_node:main'
        ],
    },
)
