from setuptools import setup
import os
from glob import glob

package_name = 'motor_cntrl_pkg'

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
            "speech_sync = motor_cntrl_pkg.speech_sync:main",
            "motor_command = motor_cntrl_pkg.motor_command_node:main",
            "face_tracker = motor_cntrl_pkg.face_tracker:main",
            "emotion_control = motor_cntrl_pkg.emotion_control:main"
        ],
    },
)
