from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'face_recognition_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages= find_packages(),  # <== this is key
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
            'face_node = face_recognition_pkg.face_recognize_active:main',
        ],
    },
)
