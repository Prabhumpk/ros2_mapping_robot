data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),

    ('share/' + package_name, ['package.xml']),

    ('share/' + package_name + '/launch',
        ['launch/display.launch.py']),

    ('share/' + package_name + '/urdf',
        ['urdf/my_robot.urdf']),
],
