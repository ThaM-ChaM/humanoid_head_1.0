from setuptools import setup

package_name = 'ts_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'face_tracker = ts_py_pkg.face_tracker:main',
            'eye_controller = ts_py_pkg.eye_controller:main',
            'maestro_controller = ts_py_pkg.motor_command_node:main'
        ],
    },
)
